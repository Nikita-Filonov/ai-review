import pytest

from ai_review.services.llm.types import ChatResultSchema
from ai_review.services.review.gateway.llm import ReviewLLMGateway
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.llm import FakeLLMClient


@pytest.fixture
def review_llm_gateway(
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
) -> ReviewLLMGateway:
    """Fixture providing ReviewLLMGateway with fake dependencies."""
    return ReviewLLMGateway(
        llm=fake_llm_client,
        cost=fake_cost_service,
        artifacts=fake_artifacts_service,
    )


@pytest.mark.asyncio
async def test_ask_happy_path(
        review_llm_gateway: ReviewLLMGateway,
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
):
    """Should call LLM, calculate cost, save artifacts, and return text."""
    fake_llm_client.responses["chat"] = ChatResultSchema(text="FAKE_RESPONSE")

    result = await review_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")

    assert result == "FAKE_RESPONSE"
    assert any(call[0] == "chat" for call in fake_llm_client.calls)
    assert any(call[0] == "calculate" for call in fake_cost_service.calls)
    assert any(call[0] == "save_llm_interaction" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_ask_warns_on_empty_response(
        capsys,
        review_llm_gateway: ReviewLLMGateway,
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
):
    """Should warn if LLM returns an empty response."""
    fake_llm_client.responses["chat"] = ChatResultSchema(text="")

    result = await review_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    output = capsys.readouterr().out

    assert result == ""
    assert "LLM returned an empty response" in output

    assert any(call[0] == "chat" for call in fake_llm_client.calls)
    assert any(call[0] == "calculate" for call in fake_cost_service.calls)
    assert any(call[0] == "save_llm_interaction" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_ask_handles_llm_error(
        capsys,
        fake_llm_client: FakeLLMClient,
        review_llm_gateway: ReviewLLMGateway,
):
    """Should handle exceptions gracefully and log error."""

    async def failing_chat(prompt: str, prompt_system: str):
        raise RuntimeError("LLM connection failed")

    fake_llm_client.chat = failing_chat

    result = await review_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    output = capsys.readouterr().out

    assert result is None
    assert "LLM request failed" in output
    assert "RuntimeError" in output
