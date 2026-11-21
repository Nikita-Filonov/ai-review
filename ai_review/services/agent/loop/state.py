from dataclasses import dataclass, field

from ai_review.services.agent.loop.schema import AgentAction, AgentLoopResultSchema, AgentStepSchema, AgentTraceSchema
from ai_review.services.llm.types import ChatResultSchema


@dataclass
class AgentRunState:
    traces: list[AgentTraceSchema] = field(default_factory=list)
    signatures: set[str] = field(default_factory=set)
    context_used: int = 0
    protocol_violations: int = 0

    def record_trace(self, trace: AgentTraceSchema, chat: ChatResultSchema) -> None:
        """Record command context and charge each LLM iteration only on its first trace."""
        first_in_iteration = not self.traces or self.traces[-1].iteration != trace.iteration
        trace.total_tokens = chat.total_tokens if first_in_iteration else None
        trace.prompt_tokens = chat.prompt_tokens if first_in_iteration else None
        trace.completion_tokens = chat.completion_tokens if first_in_iteration else None
        self.traces.append(trace)
        self.context_used += len(trace.tool_output or "")

    def finish(
            self,
            chat: ChatResultSchema,
            iteration: int,
            step: AgentStepSchema | None,
            stop_reason: str,
            warning: str | None = None,
    ) -> AgentLoopResultSchema:
        final_text = chat.text
        if step is not None and step.action.is_final:
            if step.content is None:
                raise ValueError("A FINAL step must contain content")
            final_text = step.content

        trace = AgentTraceSchema(
            step=step or AgentStepSchema(action=AgentAction.FINAL, content=chat.text or "Empty model response"),
            iteration=iteration,
            raw_output=chat.text,
        )
        if warning is not None:
            trace.warning = warning
        self.record_trace(trace, chat=chat)
        return AgentLoopResultSchema(traces=self.traces, final_text=final_text, stop_reason=stop_reason)
