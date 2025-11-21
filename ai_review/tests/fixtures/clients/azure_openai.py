from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.azure_openai.schema import (
    AzureOpenAIUsage,
    AzureOpenAIChoice,
    AzureOpenAIMessage,
    AzureOpenAIChatRequestSchema,
    AzureOpenAIChatResponseSchema,
)
from ai_review.clients.azure_openai.types import AzureOpenAIHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.azure_openai import (
    AzureOpenAIMetaConfig,
    AzureOpenAIHTTPClientConfig
)
from ai_review.libs.config.llm.base import AzureOpenAILLMConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.azure_openai.client import AzureOpenAILLMClient


class FakeAzureOpenAIHTTPClient(AzureOpenAIHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: AzureOpenAIChatRequestSchema) -> AzureOpenAIChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            AzureOpenAIChatResponseSchema(
                usage=AzureOpenAIUsage(
                    total_tokens=12,
                    prompt_tokens=5,
                    completion_tokens=7,
                ),
                choices=[
                    AzureOpenAIChoice(
                        index=0,
                        finish_reason="stop",
                        message=AzureOpenAIMessage(
                            role="assistant",
                            content="FAKE_AZURE_OPENAI_RESPONSE",
                        ),
                    )
                ],
            ),
        )


@pytest.fixture
def fake_azure_openai_http_client():
    return FakeAzureOpenAIHTTPClient()


@pytest.fixture
def azure_openai_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_azure_openai_http_client: FakeAzureOpenAIHTTPClient,
) -> AzureOpenAILLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.azure_openai.client.get_azure_openai_http_client",
        lambda: fake_azure_openai_http_client,
    )
    return AzureOpenAILLMClient()


@pytest.fixture
def azure_openai_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = AzureOpenAILLMConfig(
        meta=AzureOpenAIMetaConfig(),
        provider=LLMProvider.AZURE_OPENAI,
        http_client=AzureOpenAIHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://my-resource.openai.azure.com"),
            api_token=SecretStr("fake-token"),
            api_version="2024-06-01",
        ),
    )
    monkeypatch.setattr(settings, "llm", fake_config)
