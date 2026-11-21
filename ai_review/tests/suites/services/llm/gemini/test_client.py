import pytest

from ai_review.clients.gemini.schema import GeminiChatResponseSchema
from ai_review.services.llm.gemini.client import GeminiLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.gemini import FakeGeminiHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("gemini_http_client_config")
async def test_gemini_llm_chat(
        gemini_llm_client: GeminiLLMClient,
        fake_gemini_http_client: FakeGeminiHTTPClient
):
    result = await gemini_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_GEMINI_RESPONSE"
    assert result.total_tokens == 10
    assert result.prompt_tokens == 2
    assert result.completion_tokens is None

    assert fake_gemini_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("gemini_http_client_config")
async def test_chat_preserves_gemini_first_part_first_candidate(
        gemini_llm_client: GeminiLLMClient,
        fake_gemini_http_client: FakeGeminiHTTPClient,
) -> None:
    fake_gemini_http_client.responses["chat"] = GeminiChatResponseSchema.model_validate({
        "usageMetadata": {"totalTokenCount": 30, "promptTokenCount": 10, "candidatesTokenCount": 20},
        "candidates": [
            {"content": {"parts": [{"text": " first "}, {"text": "second"}]}},
            {"content": {"parts": [{"text": "ignored candidate"}]}},
        ],
    })

    result = await gemini_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == "first"
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20
