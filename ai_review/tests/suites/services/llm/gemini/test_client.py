import pytest

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
