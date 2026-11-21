import pytest

from ai_review.clients.openai.v2.schema import OpenAIResponsesResponseSchema
from ai_review.services.llm.openai.client import OpenAILLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.services.review.gateway.review_direct_llm_gateway import ReviewDirectLLMGateway
from ai_review.tests.fixtures.clients.openai import FakeOpenAIV2HTTPClient
from ai_review.tests.fixtures.services.artifacts import FakeArtifactsService
from ai_review.tests.fixtures.services.cost import FakeCostService
from ai_review.tests.fixtures.services.llm import FakeLLMClient


@pytest.mark.asyncio
async def test_ask_happy_path(
        review_direct_llm_gateway: ReviewDirectLLMGateway,
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
):
    """Should call LLM, calculate cost, save artifacts, and return text."""
    fake_llm_client.responses["chat"] = ChatResultSchema(text="FAKE_RESPONSE")

    result = await review_direct_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")

    assert result == "FAKE_RESPONSE"
    assert any(call[0] == "chat" for call in fake_llm_client.calls)
    calculate_calls = [call for call in fake_cost_service.calls if call[0] == "calculate"]
    assert len(calculate_calls) == 1
    assert calculate_calls[0][1]["result"].prompt_tokens is None
    assert calculate_calls[0][1]["result"].completion_tokens is None
    assert any(call[0] == "save_llm" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_ask_warns_on_empty_response(
        capsys: pytest.CaptureFixture,
        review_direct_llm_gateway: ReviewDirectLLMGateway,
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
        fake_artifacts_service: FakeArtifactsService,
):
    """Should warn if LLM returns an empty response."""
    fake_llm_client.responses["chat"] = ChatResultSchema(text="")

    result = await review_direct_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    output = capsys.readouterr().out

    assert result == ""
    assert "LLM returned an empty response" in output

    assert any(call[0] == "chat" for call in fake_llm_client.calls)
    assert any(call[0] == "calculate" for call in fake_cost_service.calls)
    assert any(call[0] == "save_llm" for call in fake_artifacts_service.calls)


@pytest.mark.asyncio
async def test_ask_passes_llm_tokens_to_calculate(
        review_direct_llm_gateway: ReviewDirectLLMGateway,
        fake_llm_client: FakeLLMClient,
        fake_cost_service: FakeCostService,
):
    fake_llm_client.responses["chat"] = ChatResultSchema(
        text="FAKE_RESPONSE",
        prompt_tokens=123,
        completion_tokens=77,
    )

    result = await review_direct_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")

    assert result == "FAKE_RESPONSE"
    calculate_call = next(call for call in fake_cost_service.calls if call[0] == "calculate")
    assert calculate_call[1]["result"].prompt_tokens == 123
    assert calculate_call[1]["result"].completion_tokens == 77


@pytest.mark.asyncio
async def test_ask_handles_llm_error(
        capsys: pytest.CaptureFixture,
        fake_llm_client: FakeLLMClient,
        review_direct_llm_gateway: ReviewDirectLLMGateway,
):
    """Should handle exceptions gracefully and log error."""

    async def failing_chat(prompt: str, prompt_system: str):
        raise RuntimeError("LLM connection failed")

    fake_llm_client.chat = failing_chat

    result = await review_direct_llm_gateway.ask("PROMPT", "SYSTEM_PROMPT")
    output = capsys.readouterr().out

    assert result is None
    assert "LLM request failed" in output
    assert "RuntimeError" in output


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
@pytest.mark.parametrize("texts", [
    ["  Hello", " World\n"],
    ['{"action":"TOOL_CALL","command":"ls"}', '{"action":"TOOL_CALL","command":"cat a.py"}'],
    ['{"file":"a.py",', '"line":1,"message":"review"}'],
])
async def test_responses_direct_review_keeps_combined_text_contract(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient,
        review_direct_llm_gateway: ReviewDirectLLMGateway,
        texts: list[str],
) -> None:
    fake_openai_v2_http_client.responses["chat"] = OpenAIResponsesResponseSchema.model_validate({
        "usage": {"total_tokens": 30, "input_tokens": 10, "output_tokens": 20},
        "output": [
            {"type": "reasoning", "content": [{"type": "output_text", "text": "ignored reasoning"}]},
            *[{"type": "message", "content": [{"type": "output_text", "text": text}]} for text in texts],
            {"type": "message", "content": [{"type": "refusal", "text": "ignored non-output text"}]},
        ],
    })
    review_direct_llm_gateway.llm = openai_llm_client

    result = await review_direct_llm_gateway.ask("PROMPT", "SYSTEM")

    assert result == "".join(texts).strip()
    assert len(fake_openai_v2_http_client.calls) == 1
