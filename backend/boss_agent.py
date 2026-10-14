from pathlib import Path

from team import register_agent

agent = register_agent("Boss", Path(__file__).parent.joinpath("prompts", "boss.md").read_text(encoding="utf-8"))
