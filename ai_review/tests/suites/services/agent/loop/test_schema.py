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


def test_agent_step_coerces_list_content_to_json_string() -> None:
    step = AgentStepSchema(action=AgentAction.FINAL, content=[{"file": "a.py", "line": 1}])
    assert step.content == '[{"file": "a.py", "line": 1}]'


def test_agent_step_coerces_dict_content_to_json_string() -> None:
    step = AgentStepSchema(action=AgentAction.FINAL, content={"summary": "No issues"})
    assert step.content == '{"summary": "No issues"}'


def test_agent_step_coerces_empty_list_content_to_json_string() -> None:
    step = AgentStepSchema(action=AgentAction.FINAL, content=[])
    assert step.content == "[]"


def test_agent_step_coerces_nested_content_to_json_string() -> None:
    step = AgentStepSchema(
        action=AgentAction.FINAL,
        content=[{"file": "a.py", "nested": {"key": [1, 2]}}],
    )
    assert '"nested"' in step.content
    assert '"key"' in step.content


def test_agent_step_coerces_numeric_content_to_json_string() -> None:
    step = AgentStepSchema(action=AgentAction.FINAL, content=42)
    assert step.content == "42"


def test_agent_step_coerces_boolean_content_to_json_string() -> None:
    step = AgentStepSchema(action=AgentAction.FINAL, content=True)
    assert step.content == "true"


def test_agent_step_tool_call_rejects_whitespace_only_command() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(action=AgentAction.TOOL_CALL, command="   ")


def test_agent_step_final_rejects_whitespace_only_content() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(action=AgentAction.FINAL, content="   ")


def test_agent_step_rejects_invalid_action() -> None:
    with pytest.raises(ValidationError):
        AgentStepSchema(action="UNKNOWN", content="something")


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
    assert result.total_tokens == 0
    assert result.prompt_tokens == 0
    assert result.completion_tokens == 0


def test_agent_loop_result_token_properties_sum_trace_tokens() -> None:
    result = AgentLoopResultSchema(
        final_text="ok",
        stop_reason="final",
        traces=[
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="one"),
                iteration=1,
                raw_output="one",
                total_tokens=10,
                prompt_tokens=4,
                completion_tokens=6,
            ),
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="two"),
                iteration=2,
                raw_output="two",
                total_tokens=None,
                prompt_tokens=3,
                completion_tokens=2,
            ),
        ],
    )

    assert result.total_tokens == 10
    assert result.prompt_tokens == 7
    assert result.completion_tokens == 8


def test_agent_loop_result_token_properties_ignore_missing_values() -> None:
    result = AgentLoopResultSchema(
        final_text="ok",
        stop_reason="final",
        traces=[
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="one"),
                iteration=1,
                raw_output="one",
            ),
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="two"),
                iteration=2,
                raw_output="two",
                total_tokens=0,
                prompt_tokens=0,
                completion_tokens=0,
            ),
        ],
    )

    assert result.total_tokens == 0
    assert result.prompt_tokens == 0
    assert result.completion_tokens == 0
