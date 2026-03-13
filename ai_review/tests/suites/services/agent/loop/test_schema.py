import pytest
from pydantic import ValidationError

from ai_review.services.agent.loop.schema import (
    AgentAction,
    AgentLoopResultSchema,
    AgentStepSchema,
    AgentTraceSchema,
)


def test_agent_action_is_final_property() -> None:
    assert AgentAction.FINAL.is_final is True
    assert AgentAction.TOOL_CALL.is_final is False


def test_agent_step_tool_call_requires_command() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(action=AgentAction.TOOL_CALL)


def test_agent_step_tool_call_rejects_content() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(
            action=AgentAction.TOOL_CALL,
            command="ls",
            content="not-allowed",
        )


def test_agent_step_final_requires_content() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(action=AgentAction.FINAL)


def test_agent_step_normalizes_command_and_content() -> None:
    step_tool = AgentStepSchema(action=AgentAction.TOOL_CALL, command="  ls -la  ")
    step_final = AgentStepSchema(action=AgentAction.FINAL, content="  done  ")
    assert step_tool.command == "ls -la"
    assert step_final.content == "done"


def test_agent_trace_normalizes_string_fields() -> None:
    trace = AgentTraceSchema(
        step=AgentStepSchema(action=AgentAction.TOOL_CALL, command="ls"),
        iteration=1,
        raw_output="  raw  ",
        tool_output="  out  ",
        warning="  warn  ",
    )
    assert trace.raw_output == "raw"
    assert trace.tool_output == "out"
    assert trace.warning == "warn"


def test_agent_loop_result_defaults_to_empty_traces() -> None:
    result = AgentLoopResultSchema(final_text="ok", stop_reason="final")
    assert result.traces == []
