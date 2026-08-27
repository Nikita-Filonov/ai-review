import re

from ai_review.services.agent.loop.schema import AgentAction

_AGENT_ACTION_ENVELOPE_RE = re.compile(
    rf"""["']action["']\s*:\s*["']({"|".join(AgentAction)})["']""",
    re.IGNORECASE,
)


def is_attempted_action(output: str) -> bool:
    """Return whether unparseable output still carries the agent protocol envelope."""
    return bool(_AGENT_ACTION_ENVELOPE_RE.search(output or ""))
