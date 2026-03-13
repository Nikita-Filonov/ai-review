import pytest

from ai_review.services.agent.loop.schema import AgentLoopResultSchema
from ai_review.services.review.gateway.review_agent_llm_gateway import ReviewAgentLLMGateway
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.review.gateway.review_agent_llm_gateway import FakeAgentLoopService
from ai_review.tests.fixtures.services.review.gateway.review_agent_llm_gateway import FakeFallbackReviewLLMGateway


@pytest.mark.asyncio
async def test_agent_gateway_returns_agent_result(
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_artifacts_service: FakeArtifactsService,
        fake_agent_loop_service: FakeAgentLoopService,
        fake_fallback_review_llm_gateway: FakeFallbackReviewLLMGateway,
):
    fake_agent_loop_service.responses["run"] = AgentLoopResultSchema(
        final_text="AGENT_RESPONSE",
        stop_reason="final",
    )

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    assert result == "AGENT_RESPONSE"
    assert any(call[0] == "run" for call in fake_agent_loop_service.calls)
    assert any(call[0] == "save_llm" for call in fake_artifacts_service.calls)
    assert fake_fallback_review_llm_gateway.calls == []


@pytest.mark.asyncio
async def test_agent_gateway_falls_back_to_default_gateway_on_error(
        review_agent_llm_gateway: ReviewAgentLLMGateway,
        fake_agent_loop_service: FakeAgentLoopService,
        fake_fallback_review_llm_gateway: FakeFallbackReviewLLMGateway,
):
    fake_agent_loop_service.responses["raise"] = True
    fake_fallback_review_llm_gateway.responses["ask"] = "ONE_SHOT_RESPONSE"

    result = await review_agent_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    assert result == "ONE_SHOT_RESPONSE"
    assert any(call[0] == "ask" for call in fake_fallback_review_llm_gateway.calls)
