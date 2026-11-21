import json

import pytest

from ai_review.services.agent.loop.parser import AgentResponseParser
from ai_review.services.agent.loop.schema import AgentAction

TOOL_ONE = '{"action":"TOOL_CALL","command":"cat one.py"}'
TOOL_TWO = '{"action":"TOOL_CALL","command":"cat two.py"}'
FINAL = '{"action":"FINAL","content":"done"}'
MALFORMED = '{"action":"TOOL_CALL","command":"cat "broken""}'


@pytest.mark.parametrize("output", [
    TOOL_ONE,
    f"```json\n{TOOL_ONE}\n```",
    f"</think>{TOOL_ONE}",
    f"I need more context. {TOOL_ONE}",
])
def test_parse_single_tool_call(agent_response_parser: AgentResponseParser, output: str) -> None:
    steps = agent_response_parser.parse(output)

    assert len(steps) == 1
    assert steps[0].action == AgentAction.TOOL_CALL
    assert steps[0].command == "cat one.py"


def test_parse_final(agent_response_parser: AgentResponseParser) -> None:
    steps = agent_response_parser.parse(FINAL)

    assert len(steps) == 1
    assert steps[0].action == AgentAction.FINAL
    assert steps[0].content == "done"


@pytest.mark.parametrize("output", [
    TOOL_ONE + TOOL_TWO,
    f"{TOOL_ONE}\n{TOOL_TWO}",
    f"{TOOL_ONE}\nNext command:\n{TOOL_TWO}",
    f"```json\n{TOOL_ONE}\n{TOOL_TWO}\n```",
    f"```json\n{TOOL_ONE}\n```\n```json\n{TOOL_TWO}\n```",
])
def test_parse_multiple_tool_calls_in_order(agent_response_parser: AgentResponseParser, output: str) -> None:
    steps = agent_response_parser.parse(output)

    assert [step.command for step in steps] == ["cat one.py", "cat two.py"]


@pytest.mark.parametrize("invalid", [
    MALFORMED,
    '{"action":"TOOL_CALL"}',
    '{"action":"TOOL_CALL","command":" "}',
    '{"action":"TOOL_CALL","command":"ls","content":"unexpected"}',
    '{"action":"UNKNOWN","command":"ls"}',
    '{"action":"FINAL"}',
    '{"action":"FINAL","content":"one"}{"action":"FINAL","content":"two"}',
])
def test_parse_rejects_entire_invalid_batch(agent_response_parser: AgentResponseParser, invalid: str) -> None:
    assert agent_response_parser.parse(TOOL_ONE + invalid) == []
    assert agent_response_parser.parse(invalid + TOOL_ONE) == []
    assert agent_response_parser.parse(FINAL + invalid) == []
    assert agent_response_parser.parse(invalid + FINAL) == []


@pytest.mark.parametrize("output", ["", "# Summary\nNo issues", '[{"file":"a.py","line":1}]'])
def test_parse_leaves_unstructured_output_to_the_loop(
        monkeypatch: pytest.MonkeyPatch,
        agent_response_parser: AgentResponseParser,
        output: str,
) -> None:
    monkeypatch.setattr(
        agent_response_parser.json_parser,
        "parse_output",
        lambda _: pytest.fail("Direct task output must not be parsed as an agent action"),
    )

    assert agent_response_parser.parse(output) == []


def test_batch_parser_preserves_braces_quotes_and_nested_final_content(agent_response_parser: AgentResponseParser) -> None:
    command = 'grep -n "{value}" file.py'
    tool = json.dumps({"action": "TOOL_CALL", "command": command})
    final = json.dumps({"action": "FINAL", "content": [{"message": "nested {json}"}]})

    steps = agent_response_parser.parse(tool + final)

    assert len(steps) == 2
    assert steps[0].command == command
    assert json.loads(steps[1].content) == [{"message": "nested {json}"}]


def test_single_step_json_repair_cannot_hide_another_malformed_action(agent_response_parser: AgentResponseParser) -> None:
    repairable = '```json\n{"action":"TOOL_CALL","command":"cat\none.py"}\n```'
    malformed = f"```json\n{MALFORMED}\n```"

    assert agent_response_parser.parse(repairable)[0].command == "cat\none.py"
    assert agent_response_parser.parse(repairable + malformed) == []
    assert agent_response_parser.parse(malformed + repairable) == []
