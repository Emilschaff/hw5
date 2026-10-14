from pathlib import Path

from team import register_agent

agent = register_agent("Inventory", Path(__file__).parent.joinpath("prompts", "inventory.md").read_text(encoding="utf-8"))
