"""Shared structured contracts for the Campus Customs agent team."""

from typing import Any, Literal

from pydantic import BaseModel, Field


AgentName = Literal["Boss", "Inventory", "Accounting", "Facilities", "Customer Service"]


class AgentDeps(BaseModel):
    agent_name: AgentName
    delegation_budget: int = Field(default=2, ge=0, le=2)


class AgentReply(BaseModel):
    answer: str
    next_agent: AgentName | None = None
    needs_approval: bool = False
    evidence: list[str] = Field(default_factory=list)


class AuditEntry(BaseModel):
    timestamp: str
    agent: AgentName
    action: str
    target: str | None = None
    result: str


class MCPToolResult(BaseModel):
    tool: str
    ticket_id: int | None = None
    data: dict[str, Any] | list[dict[str, Any]]
