"""Append-only audit trail for agent loop steps."""

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from models import AgentName, AuditEntry


AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
_LOCK = Lock()


def audit(agent: AgentName, action: str, result: str, target: str | None = None) -> None:
    entry = AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        agent=agent,
        action=action,
        target=target,
        result=result[:500],
    ).model_dump()
    with _LOCK:
        if AUDIT_PATH.exists():
            try:
                entries = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise RuntimeError(f"Audit trail is not valid JSON: {AUDIT_PATH}")
        else:
            entries = []
        if not isinstance(entries, list):
            raise RuntimeError(f"Audit trail must contain a JSON array: {AUDIT_PATH}")
        entries.append(entry)
        AUDIT_PATH.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
