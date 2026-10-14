from pathlib import Path

from team import register_agent

agent = register_agent("Accounting", Path(__file__).parent.joinpath("prompts", "accounting.md").read_text(encoding="utf-8"))
