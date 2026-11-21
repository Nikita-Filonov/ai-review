from unittest.mock import AsyncMock

import pytest

from ai_review.services.agent.loop.schema import AgentAction, AgentStepSchema, AgentTraceSchema
from ai_review.services.agent.loop.schema import AgentLoopResultSchema
from ai_review.services.agent.loop.service import AgentLoopService
from ai_review.services.agent.tool.service import AgentToolService
from ai_review.services.llm.types import ChatResultSchema
from ai_review.services.prompt.tools import format_traces
from ai_review.services.review.gateway.review_agent_llm_gateway import ReviewAgentLLMGateway
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.policy import FakePolicyService
from ai_review.tests.fixtures.services.review.gateway.review_agent_llm_gateway import FakeAgentLoopService
from ai_review.tests.fixtures.services.review.gateway.review_agent_llm_gateway import FakeFallbackReviewLLMGateway


@pytest.mark.asyncio
async def test_agent_gateway_returns_agent_result(
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
        fake_agent_loop_service: FakeAgentLoopService,
        fake_fallback_review_llm_gateway: FakeFallbackReviewLLMGateway,
):
    fake_agent_loop_service.responses["run"] = AgentLoopResultSchema(
        final_text="AGENT_RESPONSE",
        stop_reason="final",
        traces=[
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="step-one"),
                iteration=1,
                raw_output="raw-step-one",
                prompt_tokens=11,
                completion_tokens=7,
                total_tokens=18,
            ),
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="step-two"),
                iteration=2,
                raw_output="raw-step-two",
                prompt_tokens=5,
                completion_tokens=3,
                total_tokens=8,
            ),
        ],
    )

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    assert result == "AGENT_RESPONSE"
    assert any(call[0] == "run" for call in fake_agent_loop_service.calls)
    calculate_calls = [call for call in fake_cost_service.calls if call[0] == "calculate"]
    assert len(calculate_calls) == 1
    assert calculate_calls[0][1]["result"].prompt_tokens == 16
    assert calculate_calls[0][1]["result"].completion_tokens == 10
    assert any(call[0] == "save_llm" for call in fake_artifacts_service.calls)
    save_call = next(call for call in fake_artifacts_service.calls if call[0] == "save_llm")
    assert save_call[1]["cost_report"] is not None
    assert fake_fallback_review_llm_gateway.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("fallback_response", ["ONE_SHOT_RESPONSE", None])
async def test_agent_gateway_falls_back_to_default_gateway_on_error(
        fallback_response: str | None,
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_agent_loop_service: FakeAgentLoopService,
        fake_fallback_review_llm_gateway: FakeFallbackReviewLLMGateway,
):
    fake_agent_loop_service.responses["raise"] = True
    fake_fallback_review_llm_gateway.responses["ask"] = fallback_response

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    assert result == fallback_response
    assert any(call[0] == "ask" for call in fake_fallback_review_llm_gateway.calls)


@pytest.mark.asyncio
async def test_agent_gateway_calculates_zero_cost_for_missing_trace_tokens(
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_cost_service: FakeCostService,
        fake_agent_loop_service: FakeAgentLoopService,
):
    fake_agent_loop_service.responses["run"] = AgentLoopResultSchema(
        final_text="AGENT_RESPONSE",
        stop_reason="final",
        traces=[
            AgentTraceSchema(
                step=AgentStepSchema(action=AgentAction.FINAL, content="done"),
                iteration=1,
                raw_output="raw",
            ),
        ],
    )

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")

    assert result == "AGENT_RESPONSE"
    calculate_calls = [call for call in fake_cost_service.calls if call[0] == "calculate"]
    assert len(calculate_calls) == 1
    assert calculate_calls[0][1]["result"].prompt_tokens == 0
    assert calculate_calls[0][1]["result"].completion_tokens == 0


@pytest.mark.asyncio
async def test_batch_preserves_tool_policy_and_gateway_cost_accounting(
        monkeypatch: pytest.MonkeyPatch,
        agent_loop_service: AgentLoopService,
        agent_tool_service: AgentToolService,
        fake_policy_service: FakePolicyService,
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_cost_service: FakeCostService,
) -> None:
    tool_one = '{"action":"TOOL_CALL","command":"cat one.py"}'
    tool_two = '{"action":"TOOL_CALL","command":"cat two.py"}'
    final = '{"action":"FINAL","content":"done"}'
    fake_policy_service.responses["should_agent_run_command"] = False
    agent_loop_service.agent_tool = agent_tool_service
    review_agent_llm_gateway.agent_loop = agent_loop_service
    chat = AsyncMock(side_effect=[
        ChatResultSchema(text=tool_one + tool_two, prompt_tokens=10, completion_tokens=20),
        ChatResultSchema(text=final, prompt_tokens=5, completion_tokens=10),
    ])
    monkeypatch.setattr(agent_loop_service.llm, "chat", chat)
    monkeypatch.setattr(
        agent_loop_service.prompt, "build_agent_request", lambda **kwargs: format_traces(kwargs["traces"]),
    )

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM")

    assert result == "done"
    assert fake_policy_service.calls == [
        ("should_agent_run_command", {"command": "cat one.py"}),
        ("should_agent_run_command", {"command": "cat two.py"}),
    ]
    assert chat.await_args_list[1].kwargs["prompt"].count("blocked by policy") == 2
    assert len(fake_cost_service.calculated_results) == 1
    assert fake_cost_service.calculated_results[0].prompt_tokens == 15
    assert fake_cost_service.calculated_results[0].completion_tokens == 30
