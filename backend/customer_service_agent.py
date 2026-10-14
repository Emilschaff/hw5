from pathlib import Path

from team import register_agent

agent = register_agent("Customer Service", Path(__file__).parent.joinpath("prompts", "customer_service.md").read_text(encoding="utf-8"))
