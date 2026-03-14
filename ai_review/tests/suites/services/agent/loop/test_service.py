import pytest

from ai_review.services.agent.loop.service import AgentLoopService
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.services.agent.tool import FakeAgentToolService
from ai_review.tests.fixtures.services.llm import FakeLLMClient
from ai_review.tests.fixtures.services.prompt import FakePromptService


def sequence_chat(outputs: list[str]):
    async def chat(prompt: str, prompt_system: str) -> ChatResultSchema:
        return ChatResultSchema(text=outputs.pop(0))

    return chat


def sequence_chat_results(outputs: list[ChatResultSchema]):
    async def chat(prompt: str, prompt_system: str) -> ChatResultSchema:
        return outputs.pop(0)

    return chat


@pytest.mark.asyncio
async def test_run_returns_final_when_llm_returns_final(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat(['{"action":"FINAL","content":"done"}']),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "done"
    assert result.stop_reason == "final"
    assert len(result.traces) == 1
    assert fake_agent_tool_service.calls == []


@pytest.mark.asyncio
async def test_run_returns_unstructured_response_when_json_parse_fails(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat(["not-json"]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "unstructured_response"
    assert result.final_text == "not-json"
    assert "Failed to parse structured action" in (result.traces[0].warning or "")
    assert fake_agent_tool_service.calls == []


@pytest.mark.asyncio
async def test_run_executes_tool_call_then_returns_final(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"rg foo src"}',
            '{"action":"FINAL","content":"review-complete"}',
        ]),
    )
    fake_agent_tool_service.responses["execute"] = "match-line"

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "final"
    assert result.final_text == "review-complete"
    assert len(result.traces) == 2
    assert fake_agent_tool_service.calls == [("execute", {"command": "rg foo src"})]
    assert result.traces[0].tool_output == "match-line"


@pytest.mark.asyncio
async def test_run_blocks_duplicate_tool_call_signature(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"FINAL","content":"done"}',
        ]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "done"
    assert len(fake_agent_tool_service.calls) == 1
    assert "Duplicate tool call blocked" in (result.traces[1].warning or "")


@pytest.mark.asyncio
async def test_run_forces_final_when_context_limit_reached(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"cat big.txt"}',
            '{"action":"FINAL","content":"forced-final"}',
        ]),
    )
    fake_agent_tool_service.responses["execute"] = "0123456789"
    agent_loop_service.max_context_chars = 1

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "max_requests_or_context_limit"
    assert result.final_text == "forced-final"
    assert any(
        call[0] == "build_agent_request" and call[1]["force_final"] is True
        for call in fake_prompt_service.calls
    )


@pytest.mark.asyncio
async def test_force_final_returns_raw_when_forced_response_is_not_final_json(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"cat big.txt"}',
            '{"action":"TOOL_CALL","command":"cat big.txt"}',
        ]),
    )
    fake_agent_tool_service.responses["execute"] = "0123456789"
    agent_loop_service.max_context_chars = 1

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "max_requests_or_context_limit"
    assert result.final_text == '{"action":"TOOL_CALL","command":"cat big.txt"}'


@pytest.mark.asyncio
async def test_run_clears_internal_state_between_runs(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"FINAL","content":"one"}',
        ]),
    )
    await agent_loop_service.run("PROMPT", "SYSTEM")

    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"FINAL","content":"two"}',
        ]),
    )
    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "two"
    assert fake_agent_tool_service.calls.count(("execute", {"command": "ls"})) == 2


@pytest.mark.asyncio
async def test_run_forces_final_when_max_iterations_reached(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"TOOL_CALL","command":"cat a.py"}',
            '{"action":"FINAL","content":"forced"}',
        ]),
    )
    agent_loop_service.max_iterations = 2

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "max_requests_or_context_limit"
    assert result.final_text == "forced"
    assert any(
        call[0] == "build_agent_request" and call[1]["force_final"] is True
        for call in fake_prompt_service.calls
    )


@pytest.mark.asyncio
async def test_run_handles_coerced_list_content_as_final(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat(['{"action":"FINAL","content":[]}']),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "final"
    assert result.final_text == "[]"


@pytest.mark.asyncio
async def test_run_handles_empty_llm_response(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([""]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "unstructured_response"
    assert result.final_text == ""
    assert result.traces[0].step.content == "Empty model response"


@pytest.mark.asyncio
async def test_run_persists_llm_tokens_in_traces(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat_results([
            ChatResultSchema(
                text='{"action":"TOOL_CALL","command":"ls"}',
                total_tokens=30,
                prompt_tokens=10,
                completion_tokens=20,
            ),
            ChatResultSchema(
                text='{"action":"FINAL","content":"done"}',
                total_tokens=15,
                prompt_tokens=5,
                completion_tokens=10,
            ),
        ]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "done"
    assert result.traces[0].prompt_tokens == 10
    assert result.traces[0].completion_tokens == 20
    assert result.traces[1].prompt_tokens == 5
    assert result.traces[1].completion_tokens == 10
    assert result.prompt_tokens == 15
    assert result.completion_tokens == 30
    assert result.total_tokens == 45
