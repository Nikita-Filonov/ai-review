from dataclasses import dataclass, field

from ai_review.services.agent.loop.schema import AgentTraceSchema


@dataclass
class AgentRunState:
    traces: list[AgentTraceSchema] = field(default_factory=list)
    signatures: set[str] = field(default_factory=set)
    context_used: int = 0
    protocol_violations: int = 0
