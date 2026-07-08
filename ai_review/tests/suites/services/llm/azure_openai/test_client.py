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


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_openai_http_client_config")
async def test_azure_openai_llm_chat_sends_max_completion_tokens_when_set(
        azure_openai_llm_client: AzureOpenAILLMClient,
        fake_azure_openai_http_client: FakeAzureOpenAIHTTPClient,
        monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_tokens", None)
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_completion_tokens", 777)

    await azure_openai_llm_client.chat("prompt", "prompt_system")

    request = fake_azure_openai_http_client.calls[0][1]["request"]
    assert request.max_tokens is None
    assert request.max_completion_tokens == 777


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_openai_http_client_config")
async def test_azure_openai_llm_chat_sends_max_tokens_when_no_max_completion_tokens(
        azure_openai_llm_client: AzureOpenAILLMClient,
        fake_azure_openai_http_client: FakeAzureOpenAIHTTPClient,
        monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_tokens", 444)
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_completion_tokens", None)

    await azure_openai_llm_client.chat("prompt", "prompt_system")

    request = fake_azure_openai_http_client.calls[0][1]["request"]
    assert request.max_tokens == 444
    assert request.max_completion_tokens is None


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_openai_http_client_config")
async def test_azure_openai_llm_chat_sends_no_token_limits_when_both_none(
        azure_openai_llm_client: AzureOpenAILLMClient,
        fake_azure_openai_http_client: FakeAzureOpenAIHTTPClient,
        monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_tokens", None)
    monkeypatch.setattr("ai_review.config.settings.llm.meta.max_completion_tokens", None)

    await azure_openai_llm_client.chat("prompt", "prompt_system")

    request = fake_azure_openai_http_client.calls[0][1]["request"]
    assert request.max_tokens is None
    assert request.max_completion_tokens is None
