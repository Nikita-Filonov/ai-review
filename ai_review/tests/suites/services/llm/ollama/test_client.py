import pytest

from ai_review.services.llm.ollama.client import OllamaLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.ollama import FakeOllamaHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("ollama_http_client_config")
async def test_ollama_llm_chat(
        ollama_llm_client: OllamaLLMClient,
        fake_ollama_http_client: FakeOllamaHTTPClient
):
    result = await ollama_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OLLAMA_RESPONSE"
    assert result.total_tokens == 8
    assert result.prompt_tokens == 3
    assert result.completion_tokens == 5

    assert fake_ollama_http_client.calls[0][0] == "chat"
