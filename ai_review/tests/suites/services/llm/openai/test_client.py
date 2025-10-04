import pytest

from ai_review.services.llm.openai.client import OpenAILLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.openai import FakeOpenAIHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_http_client_config")
async def test_openai_llm_chat(
        openai_llm_client: OpenAILLMClient,
        fake_openai_http_client: FakeOpenAIHTTPClient
):
    result = await openai_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OPENAI_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_openai_http_client.calls[0][0] == "chat"
