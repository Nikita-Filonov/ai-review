import asyncio

import pytest

from ai_review.config import settings
from ai_review.services.agent.loop.schema import AgentAction, AgentStepSchema, AgentTraceSchema
from ai_review.services.agent.loop.service import AgentLoopService
from ai_review.services.agent.loop.state import AgentRunState
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


MALFORMED_TOOL_CALL = '{"action":"TOOL_CALL","command":"git grep -n -i -l "migration" -- docs"}'
REASONING_PREFIXED_TOOL_CALL = '</think>{"action":"TOOL_CALL","command":"cat modules/Sample.java"}'
PROSE_WRAPPED_TOOL_CALL = (
    'Let me examine the key files first.{"action":"TOOL_CALL","command":"cat modules/Sample.java"}'
)
MARKDOWN_SUMMARY = "## Summary\n\n- The change looks correct.\n\n```python\nprint(1)\n```\n"
INLINE_COMMENTS_JSON = '[{"file":"a.py","line":10,"message":"Unused import","suggestion":null}]'


def test_service_uses_configured_protocol_violation_limit(
        monkeypatch: pytest.MonkeyPatch,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(settings.agent, "max_protocol_violations", 7)

    service = AgentLoopService(
        llm=fake_llm_client,
        prompt=fake_prompt_service,
        agent_tool=fake_agent_tool_service,
    )

    assert service.max_protocol_violations == 7


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
async def test_run_rejects_final_step_without_content_from_parser(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    invalid_final = AgentStepSchema.model_construct(
        action=AgentAction.FINAL,
        command=None,
        content=None,
    )
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat(['{"action":"FINAL"}']))
    monkeypatch.setattr(agent_loop_service.parser, "parse_output", lambda _: invalid_final)

    with pytest.raises(ValueError, match="FINAL step must contain content"):
        await agent_loop_service.run("PROMPT", "SYSTEM")

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
    assert "without an agent envelope" in (result.traces[0].warning or "")
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
async def test_run_step_rejects_step_without_command(
        agent_loop_service: AgentLoopService,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    final_step = AgentStepSchema(action=AgentAction.FINAL, content="done")
    chat = ChatResultSchema(text='{"action":"FINAL","content":"done"}')
    state = AgentRunState()

    with pytest.raises(ValueError, match="TOOL_CALL step must contain a command"):
        await agent_loop_service.run_step(step=final_step, chat=chat, state=state, iteration=1)

    assert state.signatures == set()
    assert fake_agent_tool_service.calls == []


@pytest.mark.asyncio
async def test_run_executes_tool_call_embedded_in_model_reasoning(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            '</think>{"action":"TOOL_CALL","command":"cat modules/Example.java"}',
            'The review is complete. {"action":"FINAL","content":"done"}',
        ]),
    )
    fake_agent_tool_service.responses["execute"] = "file-content"

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "final"
    assert result.final_text == "done"
    assert fake_agent_tool_service.calls == [
        ("execute", {"command": "cat modules/Example.java"}),
    ]
    assert result.traces[0].tool_output == "file-content"


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
async def test_force_final_returns_raw_unparseable_action(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat([MALFORMED_TOOL_CALL]))
    result = await agent_loop_service.force_final("PROMPT", "SYSTEM", state=AgentRunState())
    assert result.final_text == MALFORMED_TOOL_CALL
    assert result.traces[0].raw_output == MALFORMED_TOOL_CALL


@pytest.mark.asyncio
async def test_force_final_handles_empty_response(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat([""]))

    result = await agent_loop_service.force_final("PROMPT", "SYSTEM", state=AgentRunState())

    assert result.stop_reason == "max_requests_or_context_limit"
    assert result.final_text == ""
    assert result.traces[0].raw_output == ""
    assert result.traces[0].step is not None
    assert result.traces[0].step.action is AgentAction.FINAL
    assert result.traces[0].step.content == "Empty model response"


@pytest.mark.asyncio
async def test_force_final_accepts_direct_task_output_without_action_parse(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat([INLINE_COMMENTS_JSON]))
    monkeypatch.setattr(
        agent_loop_service.parser,
        "parse_output",
        lambda _: pytest.fail("Direct task output must not be parsed as an agent action"),
    )

    result = await agent_loop_service.force_final("PROMPT", "SYSTEM", state=AgentRunState())

    assert result.final_text == INLINE_COMMENTS_JSON


@pytest.mark.asyncio
async def test_run_keeps_state_separate_between_runs(
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
    first = await agent_loop_service.run("PROMPT", "SYSTEM")

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
    assert first.final_text == "one"
    assert len(first.traces) == len(result.traces) == 2
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


@pytest.mark.asyncio
async def test_run_retries_when_attempted_action_is_malformed(
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
            MALFORMED_TOOL_CALL,
            '{"action":"FINAL","content":"review-complete"}',
        ]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "final"
    assert result.final_text == "review-complete"
    assert MALFORMED_TOOL_CALL not in result.final_text
    assert len(result.traces) == 2
    assert result.traces[0].step is None
    assert result.traces[0].raw_output == MALFORMED_TOOL_CALL
    assert "Invalid response discarded" in (result.traces[0].warning or "")
    assert fake_agent_tool_service.calls == []
    assert [
        call[1]["force_final"] for call in fake_prompt_service.calls
        if call[0] == "build_agent_request"
    ] == [False, False]


@pytest.mark.asyncio
async def test_run_does_not_execute_the_command_of_a_malformed_action(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            MALFORMED_TOOL_CALL,
            '{"action":"TOOL_CALL","command":"ls"}',
            '{"action":"FINAL","content":"done"}',
        ]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "done"
    assert fake_agent_tool_service.calls == [("execute", {"command": "ls"})]


@pytest.mark.asyncio
async def test_run_counts_tokens_of_a_discarded_attempted_action(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat_results([
            ChatResultSchema(
                text=MALFORMED_TOOL_CALL,
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
    assert result.total_tokens == 45


@pytest.mark.parametrize("max_protocol_violations", [0, 1, 2])
@pytest.mark.asyncio
async def test_run_honors_malformed_action_budget(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        max_protocol_violations: int,
) -> None:
    malformed_responses = [MALFORMED_TOOL_CALL] * (max_protocol_violations + 1)
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat(malformed_responses + ['{"action":"FINAL","content":"forced-final"}']),
    )
    agent_loop_service.max_protocol_violations = max_protocol_violations

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "max_requests_or_context_limit"
    assert result.final_text == "forced-final"
    assert MALFORMED_TOOL_CALL not in result.final_text
    assert sum(trace.step is None for trace in result.traces) == max_protocol_violations + 1
    assert len(result.traces) == max_protocol_violations + 2
    assert [
        call[1]["force_final"]
        for call in fake_prompt_service.calls
        if call[0] == "build_agent_request"
    ] == [False] * (max_protocol_violations + 1) + [True]


@pytest.mark.asyncio
async def test_run_resets_the_malformed_action_budget_between_runs(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    for expected in ("one", "two"):
        monkeypatch.setattr(
            fake_llm_client,
            "chat",
            sequence_chat([
                MALFORMED_TOOL_CALL,
                MALFORMED_TOOL_CALL,
                f'{{"action":"FINAL","content":"{expected}"}}',
            ]),
        )

        result = await agent_loop_service.run("PROMPT", "SYSTEM")

        assert result.stop_reason == "final"
        assert result.final_text == expected


@pytest.mark.asyncio
async def test_run_returns_markdown_summary_as_final_text(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat([MARKDOWN_SUMMARY]))
    monkeypatch.setattr(
        agent_loop_service.parser,
        "parse_output",
        lambda _: pytest.fail("Direct task output must not be parsed as an agent action"),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "unstructured_response"
    assert result.final_text == MARKDOWN_SUMMARY
    assert len(result.traces) == 1


@pytest.mark.asyncio
async def test_run_returns_inline_comment_json_array_as_final_text(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(fake_llm_client, "chat", sequence_chat([INLINE_COMMENTS_JSON]))
    monkeypatch.setattr(
        agent_loop_service.parser,
        "parse_output",
        lambda _: pytest.fail("Direct task output must not be parsed as an agent action"),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "unstructured_response"
    assert result.final_text == INLINE_COMMENTS_JSON
    assert len(result.traces) == 1


@pytest.mark.parametrize("shared_command", [False, True])
@pytest.mark.parametrize("max_iterations", [1, 2])
@pytest.mark.asyncio
async def test_concurrent_runs_keep_agent_histories_separate(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_prompt_service: FakePromptService,
        fake_agent_tool_service: FakeAgentToolService,
        shared_command: bool,
        max_iterations: int,
) -> None:
    first_requests = 0
    both_started = asyncio.Event()
    histories: list[tuple[str, tuple[str, ...], bool]] = []
    commands = {
        task: "cat shared.txt" if shared_command else f"cat {task}"
        for task in ("first", "second")
    }
    agent_loop_service.max_iterations = max_iterations

    def build_agent_request(
            *,
            traces: list[AgentTraceSchema],
            force_final: bool,
            original_prompt: str,
            original_prompt_system: str,
    ) -> str:
        history = tuple(trace.step.command for trace in traces if trace.step and trace.step.command)
        histories.append((original_prompt, history, force_final))
        return f"{original_prompt}:{len(traces)}"

    async def chat(prompt: str, prompt_system: str) -> ChatResultSchema:
        nonlocal first_requests
        task, iteration = prompt.split(":")
        prompt_tokens = 10 if task == "first" else 20
        if iteration == "0":
            first_requests += 1
            if first_requests == 2:
                both_started.set()
            await both_started.wait()
            return ChatResultSchema(
                text=f'{{"action":"TOOL_CALL","command":"{commands[task]}"}}',
                prompt_tokens=prompt_tokens,
                completion_tokens=1,
            )
        return ChatResultSchema(
            text=f'{{"action":"FINAL","content":"done {task}"}}',
            prompt_tokens=prompt_tokens,
            completion_tokens=2,
        )

    monkeypatch.setattr(fake_prompt_service, "build_agent_request", build_agent_request)
    monkeypatch.setattr(fake_llm_client, "chat", chat)

    first, second = await asyncio.wait_for(
        asyncio.gather(
            agent_loop_service.run("first", "SYSTEM"),
            agent_loop_service.run("second", "SYSTEM"),
        ),
        timeout=5,
    )

    assert first.final_text == "done first"
    assert second.final_text == "done second"
    assert first.prompt_tokens == 20
    assert second.prompt_tokens == 40
    assert first.completion_tokens == second.completion_tokens == 3
    assert len(fake_agent_tool_service.calls) == 2
    for task, result in (("first", first), ("second", second)):
        assert [
            (history, forced) for name, history, forced in histories if name == task
        ] == [((), False), ((commands[task],), max_iterations == 1)]
        assert [trace.step.command for trace in result.traces if trace.step and trace.step.command] == [commands[task]]
        assert result.stop_reason == ("max_requests_or_context_limit" if max_iterations == 1 else "final")


@pytest.mark.asyncio
async def test_run_recovers_from_reasoning_delimiter_before_the_action(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
        fake_agent_tool_service: FakeAgentToolService,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            REASONING_PREFIXED_TOOL_CALL,
            '{"action":"TOOL_CALL","command":"cat modules/Sample.java"}',
            '{"action":"FINAL","content":"review-complete"}',
        ]),
    )
    fake_agent_tool_service.responses["execute"] = "class Sample {}"

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.stop_reason == "final"
    assert result.final_text == "review-complete"
    assert fake_agent_tool_service.calls == [("execute", {"command": "cat modules/Sample.java"})]


@pytest.mark.asyncio
async def test_run_does_not_promote_prose_wrapped_action_to_final_text(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        fake_llm_client: FakeLLMClient,
) -> None:
    monkeypatch.setattr(
        fake_llm_client,
        "chat",
        sequence_chat([
            PROSE_WRAPPED_TOOL_CALL,
            '{"action":"FINAL","content":"review-complete"}',
        ]),
    )

    result = await agent_loop_service.run("PROMPT", "SYSTEM")

    assert result.final_text == "review-complete"
    assert result.final_text != PROSE_WRAPPED_TOOL_CALL
