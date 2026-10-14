"""Campus Customs MCP tools backed by the working database copy."""

from pathlib import Path
import sqlite3
from typing import Any

from fastmcp import FastMCP


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs_new.db"
mcp = FastMCP("Campus Customs Operations")


def _read_one(connection: sqlite3.Connection, query: str, parameters: tuple[Any, ...]) -> dict[str, Any]:
    row = connection.execute(query, parameters).fetchone()
    if row is None:
        raise ValueError("The requested database record does not exist.")
    return dict(row)


def _read_many(connection: sqlite3.Connection, query: str, parameters: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(query, parameters).fetchall()]


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@mcp.tool
def get_customer_order_context(ticket_id: int = 101) -> dict[str, Any]:
    """Read ticket 101's tee request, stock, price, invoice, and vendor records."""
    if ticket_id != 101:
        raise ValueError("This tool is scoped to open ticket 101.")
    with _connection() as connection:
        ticket = _read_one(connection, "SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        inventory = _read_one(
            connection,
            "SELECT * FROM inventory WHERE sku = ? AND size = ?",
            (ticket["sku"], ticket["size"]),
        )
        pricing = _read_one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
        invoice = _read_one(connection, "SELECT * FROM invoices WHERE id = ?", (ticket["invoice_id"],))
        vendor = _read_one(connection, "SELECT * FROM vendors WHERE id = ?", (invoice["vendor_id"],))
    return {"ticket": ticket, "inventory": inventory, "pricing": pricing, "invoice": invoice, "vendor": vendor}


@mcp.tool
def get_rent_payment_context(ticket_id: int = 102) -> dict[str, Any]:
    """Read ticket 102's lease, desk date, and cash-account records."""
    if ticket_id != 102:
        raise ValueError("This tool is scoped to open ticket 102.")
    with _connection() as connection:
        ticket = _read_one(connection, "SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        lease = _read_one(connection, "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],))
        desk = _read_one(connection, "SELECT * FROM desk LIMIT 1", ())
        cash_accounts = _read_many(connection, "SELECT * FROM cash_accounts", ())
        payments = _read_many(connection, "SELECT * FROM payments WHERE account IN (SELECT name FROM cash_accounts)", ())
    return {"ticket": ticket, "lease": lease, "desk": desk, "cash_accounts": cash_accounts, "payments": payments}


@mcp.tool
def get_bulk_hoodie_context(ticket_id: int = 103) -> dict[str, Any]:
    """Read ticket 103's requested hoodie quantity, size stock, and current price."""
    if ticket_id != 103:
        raise ValueError("This tool is scoped to open ticket 103.")
    with _connection() as connection:
        ticket = _read_one(connection, "SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        inventory = _read_many(connection, "SELECT * FROM inventory WHERE sku = ?", (ticket["sku"],))
        pricing = _read_one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
    return {"ticket": ticket, "inventory": inventory, "pricing": pricing}


@mcp.tool
def list_open_tickets() -> list[dict[str, Any]]:
    """List the current open tickets for Boss triage, from the working database."""
    with _connection() as connection:
        return _read_many(connection, "SELECT * FROM tickets WHERE status = 'open' ORDER BY id", ())


@mcp.tool
def get_restock_vendor_options(sku: str) -> dict[str, Any]:
    """Read vendors whose specialty and lead time can inform replenishment for a SKU."""
    with _connection() as connection:
        pricing = _read_one(connection, "SELECT * FROM pricing WHERE sku = ?", (sku,))
        vendors = _read_many(connection, "SELECT * FROM vendors WHERE specialty LIKE '%apparel%' OR specialty LIKE '%goods%' ORDER BY id", ())
    return {"pricing": pricing, "vendors": vendors}


@mcp.tool
def get_financial_obligations() -> dict[str, Any]:
    """Read open invoices, leases, cash accounts, and recorded payments for Accounting."""
    with _connection() as connection:
        return {
            "invoices": _read_many(connection, "SELECT * FROM invoices WHERE status = 'open' ORDER BY due_date", ()),
            "leases": _read_many(connection, "SELECT * FROM leases ORDER BY next_due", ()),
            "cash_accounts": _read_many(connection, "SELECT * FROM cash_accounts", ()),
            "payments": _read_many(connection, "SELECT * FROM payments ORDER BY paid_at", ()),
        }


@mcp.tool
def get_facilities_context(ticket_id: int = 102) -> dict[str, Any]:
    """Read the rent ticket, desk date, linked lease, and related payments for Facilities."""
    if ticket_id != 102:
        raise ValueError("This tool is scoped to open ticket 102.")
    with _connection() as connection:
        ticket = _read_one(connection, "SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        lease = _read_one(connection, "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],))
        desk = _read_one(connection, "SELECT * FROM desk LIMIT 1", ())
        payments = _read_many(connection, "SELECT * FROM payments WHERE kind LIKE '%rent%' OR ref_id = ?", (lease["id"],))
    return {"ticket": ticket, "lease": lease, "desk": desk, "payments": payments}


if __name__ == "__main__":
    mcp.run()
