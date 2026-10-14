"""FastAPI operations API for the Campus Customs dashboard."""

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import accounting_agent  # noqa: F401 - registers the team agent
import boss_agent  # noqa: F401 - registers the team agent
import customer_service_agent  # noqa: F401 - registers the team agent
import facilities_agent  # noqa: F401 - registers the team agent
import inventory_agent  # noqa: F401 - registers the team agent
from audit import AUDIT_PATH, audit
from models import AgentDeps, AgentName
from team import get_agent


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "campus_customs_new.db"
ORIGINAL_DB_PATH = ROOT / "data" / "campus_customs.db"
app = FastAPI(title="Campus Customs Operations API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRunRequest(BaseModel):
    agent: AgentName = "Boss"
    delegation_budget: int = Field(default=2, ge=0, le=2)


class ApprovalRequest(BaseModel):
    approved_by: str = Field(min_length=1)
    account: str = "checking"
    amount: float | None = Field(default=None, gt=0)
    kind: str = "approved_purchase"


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def rows(connection: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def describe_agent_error(error: Exception) -> str:
    """Preserve provider details instead of reducing errors to a generic message."""
    parts: list[str] = []
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        detail = getattr(current, "body", None) or getattr(current, "response", None)
        parts.append(f"{type(current).__name__}: {detail or str(current)}")
        current = current.__cause__ or current.__context__
    return " | ".join(parts)


@app.get("/api/tickets")
def list_tickets() -> dict[str, Any]:
    """Return tickets 101-103 and their current open/resolved status."""
    with db() as connection:
        tickets = rows(connection, "SELECT * FROM tickets WHERE id IN (101, 102, 103) ORDER BY id")
    return {"tickets": tickets}


@app.post("/api/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int, request: AgentRunRequest = AgentRunRequest()) -> dict[str, Any]:
    """Run the selected team agent on one open ticket; facts are obtained through MCP tools."""
    if ticket_id not in {101, 102, 103}:
        raise HTTPException(status_code=404, detail="Only tickets 101, 102, and 103 are supported.")
    with db() as connection:
        ticket = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    prompt = f"Review open ticket {ticket_id}. Use the MCP tools to gather the relevant database evidence and prepare a safe recommendation. Do not execute payments, purchases, discounts, or external communications."
    try:
        result = await get_agent(request.agent).run(
            prompt,
            deps=AgentDeps(agent_name=request.agent, delegation_budget=request.delegation_budget),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent run failed: {describe_agent_error(exc)}") from exc
    output = result.output.model_dump() if hasattr(result.output, "model_dump") else str(result.output)
    audit(request.agent, "agent_loop", f"Completed ticket {ticket_id}: {json.dumps(output)[:400]}", str(ticket_id))
    return {"ticket_id": ticket_id, "agent": request.agent, "result": output}


@app.get("/api/events")
def recent_events(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    """Return recent append-only agent audit events for dashboard refreshes."""
    if not AUDIT_PATH.exists():
        return {"events": []}
    try:
        events = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Audit trail is invalid JSON.") from exc
    return {"events": events[-limit:]}


@app.post("/api/tickets/{ticket_id}/approve")
def approve_payment(ticket_id: int, request: ApprovalRequest) -> dict[str, Any]:
    """Execute a human-approved payment/purchase and decrement the selected cash account."""
    if ticket_id not in {101, 102, 103}:
        raise HTTPException(status_code=404, detail="Only tickets 101, 102, and 103 are supported.")
    with db() as connection:
        ticket = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found.")
        if ticket["status"] == "resolved":
            raise HTTPException(status_code=409, detail="Ticket is already resolved.")
        if ticket_id == 101:
            amount_row = connection.execute("SELECT amount FROM invoices WHERE id = ?", (ticket["invoice_id"],)).fetchone()
            reference_id = ticket["invoice_id"]
            default_kind = "invoice_payment"
        elif ticket_id == 102:
            amount_row = connection.execute("SELECT monthly_rent AS amount FROM leases WHERE id = ?", (ticket["lease_id"],)).fetchone()
            reference_id = ticket["lease_id"]
            default_kind = "rent_payment"
        else:
            amount_row = None
            reference_id = ticket_id
            default_kind = "approved_purchase"
        amount = request.amount if request.amount is not None else (float(amount_row["amount"]) if amount_row else None)
        if amount is None:
            raise HTTPException(status_code=422, detail="This purchase requires an explicit approved amount.")
        account = connection.execute("SELECT * FROM cash_accounts WHERE name = ?", (request.account,)).fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Cash account not found.")
        if float(account["balance"]) < amount:
            raise HTTPException(status_code=409, detail="Payment would make the cash account negative.")
        connection.execute(
            "INSERT INTO payments (kind, ref_id, amount, account, paid_at, approved_by) VALUES (?, ?, ?, ?, ?, ?)",
            (request.kind or default_kind, reference_id, amount, request.account, datetime.now(timezone.utc).isoformat(), request.approved_by),
        )
        connection.execute("UPDATE cash_accounts SET balance = balance - ?, date = ? WHERE name = ?", (amount, datetime.now(timezone.utc).date().isoformat(), request.account))
        connection.execute("UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,))
        connection.commit()
        new_balance = connection.execute("SELECT balance FROM cash_accounts WHERE name = ?", (request.account,)).fetchone()[0]
    audit("Boss", "human_approval_executed", f"Approved {amount:.2f} from {request.account}; new balance {new_balance:.2f}.", str(ticket_id))
    return {"ticket_id": ticket_id, "payment_amount": amount, "account": request.account, "new_balance": new_balance, "status": "resolved"}


@app.get("/api/cash/checking")
def checking_balance() -> dict[str, Any]:
    """Return the current checking balance from cash_accounts."""
    with db() as connection:
        account = connection.execute("SELECT * FROM cash_accounts WHERE name = 'checking'").fetchone()
    if account is None:
        raise HTTPException(status_code=404, detail="Checking account not found.")
    return dict(account)


@app.post("/api/reset")
def reset_database() -> dict[str, str]:
    """Replace the working database with the untouched original database."""
    if not ORIGINAL_DB_PATH.exists():
        raise HTTPException(status_code=500, detail="Original database not found.")
    shutil.copy2(ORIGINAL_DB_PATH, DB_PATH)
    audit("Boss", "database_reset", "Working database restored from the original seed database.")
    return {"status": "reset", "database": str(DB_PATH)}
