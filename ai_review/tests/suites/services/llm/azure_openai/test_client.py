import pytest

from ai_review.services.llm.azure_openai.client import AzureOpenAILLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.azure_openai import FakeAzureOpenAIHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_openai_http_client_config")
async def test_azure_openai_llm_chat(
        azure_openai_llm_client: AzureOpenAILLMClient,
        fake_azure_openai_http_client: FakeAzureOpenAIHTTPClient,
):
    result = await azure_openai_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_AZURE_OPENAI_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_azure_openai_http_client.calls[0][0] == "chat"
