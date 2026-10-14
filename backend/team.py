"""Shared Portkey model setup, MCP bridge, and fully connected delegation."""

import os
from pathlib import Path
from typing import Any

from fastmcp import Client
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from audit import audit
from models import AgentDeps, AgentName, AgentReply


ROOT = Path(__file__).resolve().parent.parent
SERVER_PATH = ROOT / "mcp_server" / "server.py"
AGENT_NAMES: tuple[AgentName, ...] = ("Boss", "Inventory", "Accounting", "Facilities", "Customer Service")
_agents: dict[AgentName, Agent[AgentDeps, AgentReply]] = {}
MAX_OUTPUT_TOKENS = 1200


def portkey_model() -> OpenAIModel:
    key = os.environ.get("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is required to run an agent.")
    client = AsyncOpenAI(
        base_url="https://api.portkey.ai/v1",
        api_key=key,
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    return OpenAIModel(
        "gpt-6-luna",
        provider=OpenAIProvider(openai_client=client),
    )


async def call_mcp(agent_name: AgentName, tool: str, arguments: dict[str, Any]) -> Any:
    async with Client(SERVER_PATH) as client:
        result = await client.call_tool(tool, arguments)
    audit(agent_name, "mcp_tool", f"Called {tool}; returned structured database evidence.", tool)
    return result.data


async def delegate(ctx: RunContext[AgentDeps], target: AgentName, task: str) -> AgentReply:
    if target not in AGENT_NAMES:
        raise ValueError("Unknown agent.")
    if target == ctx.deps.agent_name:
        raise ValueError("An agent cannot delegate to itself.")
    if ctx.deps.delegation_budget <= 0:
        raise ValueError("Delegation budget exhausted; return to the caller for approval.")
    audit(ctx.deps.agent_name, "delegation", f"Delegating task: {task}", target)
    target_agent = get_agent(target)
    result = await target_agent.run(task, deps=AgentDeps(agent_name=target, delegation_budget=ctx.deps.delegation_budget - 1))
    audit(ctx.deps.agent_name, "delegation_result", "Received a bounded structured reply.", target)
    return result.output


def get_agent(name: AgentName) -> Agent[AgentDeps, AgentReply]:
    if name not in _agents:
        raise RuntimeError(f"Agent {name} has not been registered.")
    return _agents[name]


def register_agent(name: AgentName, prompt: str) -> Agent[AgentDeps, AgentReply]:
    # PydanticAI's OpenAI adapter translates this `max_tokens` setting to
    # Portkey's required `max_completion_tokens` request field.
    agent: Agent[AgentDeps, AgentReply] = Agent(
        portkey_model(),
        deps_type=AgentDeps,
        output_type=AgentReply,
        system_prompt=prompt,
        model_settings={"max_tokens": MAX_OUTPUT_TOKENS, "openai_reasoning_effort": "none"},
    )
    agent.tool(delegate)

    async def ticket_101(ctx: RunContext[AgentDeps]) -> Any:
        """Read customer order ticket 101 through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_customer_order_context", {"ticket_id": 101})

    async def ticket_102(ctx: RunContext[AgentDeps]) -> Any:
        """Read rent and payment ticket 102 through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_rent_payment_context", {"ticket_id": 102})

    async def ticket_103(ctx: RunContext[AgentDeps]) -> Any:
        """Read bulk hoodie ticket 103 through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_bulk_hoodie_context", {"ticket_id": 103})

    async def open_tickets(ctx: RunContext[AgentDeps]) -> Any:
        """Read all open tickets through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "list_open_tickets", {})

    async def restock_vendors(ctx: RunContext[AgentDeps], sku: str) -> Any:
        """Read SKU pricing and vendor options through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_restock_vendor_options", {"sku": sku})

    async def financial_obligations(ctx: RunContext[AgentDeps]) -> Any:
        """Read financial obligations through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_financial_obligations", {})

    async def facilities_context(ctx: RunContext[AgentDeps]) -> Any:
        """Read facilities context through the MCP server."""
        return await call_mcp(ctx.deps.agent_name, "get_facilities_context", {"ticket_id": 102})

    for tool in (ticket_101, ticket_102, ticket_103, open_tickets, restock_vendors, financial_obligations, facilities_context):
        agent.tool(tool)
    _agents[name] = agent
    return agent
