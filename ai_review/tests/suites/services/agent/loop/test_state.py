from ai_review.services.agent.loop.schema import AgentAction, AgentStepSchema, AgentTraceSchema
from ai_review.services.agent.loop.state import AgentRunState
from ai_review.services.llm.types import ChatResultSchema


def test_record_trace_counts_usage_once_per_response() -> None:
    state = AgentRunState()
    chat = ChatResultSchema(text="batch", total_tokens=30, prompt_tokens=10, completion_tokens=20)
    first = AgentTraceSchema(iteration=1, raw_output=chat.text, tool_output="first output")
    second = AgentTraceSchema(iteration=1, raw_output=chat.text, tool_output="second output")

    state.record_trace(first, chat)
    state.record_trace(second, chat)

    assert state.traces == [first, second]
    assert first.total_tokens == 30
    assert first.prompt_tokens == 10
    assert first.completion_tokens == 20
    assert second.total_tokens is None
    assert second.prompt_tokens is None
    assert second.completion_tokens is None
    assert state.context_used == len("first outputsecond output")
    assert chat.total_tokens == 30


def test_record_trace_counts_identical_usage_on_distinct_iterations() -> None:
    state = AgentRunState()
    chat = ChatResultSchema(text="same response", total_tokens=30, prompt_tokens=10, completion_tokens=20)
    first = AgentTraceSchema(iteration=1, raw_output=chat.text)
    second = AgentTraceSchema(iteration=2, raw_output=chat.text)

    state.record_trace(first, chat)
    state.record_trace(second, chat)

    assert sum(trace.total_tokens for trace in state.traces) == 60
    assert sum(trace.prompt_tokens for trace in state.traces) == 20
    assert sum(trace.completion_tokens for trace in state.traces) == 40
    assert state.context_used == 0


def test_record_trace_counts_response_even_when_first_command_is_blocked() -> None:
    state = AgentRunState()
    chat = ChatResultSchema(text="batch", total_tokens=30, prompt_tokens=10, completion_tokens=20)
    blocked = AgentTraceSchema(iteration=1, raw_output=chat.text, warning="Duplicate tool call blocked: ls")
    executed = AgentTraceSchema(iteration=1, raw_output=chat.text, tool_output="file contents")

    state.record_trace(blocked, chat)
    state.record_trace(executed, chat)

    assert blocked.total_tokens == 30
    assert executed.total_tokens is None
    assert state.context_used == len("file contents")


def test_record_trace_preserves_missing_usage() -> None:
    state = AgentRunState()
    chat = ChatResultSchema(text="done")
    trace = AgentTraceSchema(
        iteration=1,
        raw_output=chat.text,
        step=AgentStepSchema(action=AgentAction.FINAL, content="done"),
    )

    state.record_trace(trace, chat)

    assert trace.total_tokens is None
    assert trace.prompt_tokens is None
    assert trace.completion_tokens is None
    assert state.context_used == 0


def test_record_trace_keeps_runs_independent() -> None:
    first = AgentRunState()
    second = AgentRunState()
    chat = ChatResultSchema(text="tool", total_tokens=30)

    first.record_trace(AgentTraceSchema(iteration=1, raw_output=chat.text, tool_output="first output"), chat)
    second.record_trace(AgentTraceSchema(iteration=1, raw_output=chat.text, tool_output="second output"), chat)

    assert first.traces is not second.traces
    assert first.traces[0].total_tokens == second.traces[0].total_tokens == 30
    assert first.context_used == len("first output")
    assert second.context_used == len("second output")


def test_finish_includes_previous_usage_without_adding_final_content_to_context() -> None:
    state = AgentRunState()
    state.record_trace(
        AgentTraceSchema(iteration=1, raw_output="tool", tool_output="file contents"),
        ChatResultSchema(text="tool", total_tokens=30, prompt_tokens=10, completion_tokens=20),
    )
    final = AgentStepSchema(action=AgentAction.FINAL, content="done")

    result = state.finish(
        chat=ChatResultSchema(text=final.model_dump_json(), total_tokens=15, prompt_tokens=5, completion_tokens=10),
        iteration=2,
        step=final,
        stop_reason="final",
    )

    assert result.final_text == "done"
    assert result.stop_reason == "final"
    assert result.total_tokens == 45
    assert result.prompt_tokens == 15
    assert result.completion_tokens == 30
    assert result.traces[-1].warning is None
    assert state.context_used == len("file contents")


def test_finish_preserves_unstructured_text_and_warning() -> None:
    state = AgentRunState()
    chat = ChatResultSchema(text="  raw answer\n", total_tokens=15)

    result = state.finish(
        chat=chat,
        iteration=1,
        step=None,
        stop_reason="unstructured_response",
        warning="Model returned content without an agent envelope.",
    )

    assert result.final_text == "  raw answer\n"
    assert result.stop_reason == "unstructured_response"
    assert result.traces[0].step.content == "raw answer"
    assert result.traces[0].warning == "Model returned content without an agent envelope."
    assert result.total_tokens == 15
    assert state.context_used == 0
