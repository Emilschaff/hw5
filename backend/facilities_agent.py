from pathlib import Path

from team import register_agent

agent = register_agent("Facilities", Path(__file__).parent.joinpath("prompts", "facilities.md").read_text(encoding="utf-8"))
