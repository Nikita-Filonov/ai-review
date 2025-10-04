from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.openai.schema import (
    OpenAIUsageSchema,
    OpenAIChoiceSchema,
    OpenAIMessageSchema,
    OpenAIChatRequestSchema,
    OpenAIChatResponseSchema,
)
from ai_review.clients.openai.types import OpenAIHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import OpenAILLMConfig
from ai_review.libs.config.llm.openai import OpenAIMetaConfig, OpenAIHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.openai.client import OpenAILLMClient


class FakeOpenAIHTTPClient(OpenAIHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: OpenAIChatRequestSchema) -> OpenAIChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            OpenAIChatResponseSchema(
                usage=OpenAIUsageSchema(total_tokens=12, prompt_tokens=5, completion_tokens=7),
                choices=[
                    OpenAIChoiceSchema(
                        message=OpenAIMessageSchema(role="assistant", content="FAKE_OPENAI_RESPONSE")
                    )
                ],
            ),
        )


@pytest.fixture
def fake_openai_http_client():
    return FakeOpenAIHTTPClient()


@pytest.fixture
def openai_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_openai_http_client: FakeOpenAIHTTPClient
) -> OpenAILLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.openai.client.get_openai_http_client",
        lambda: fake_openai_http_client,
    )
    return OpenAILLMClient()


@pytest.fixture
def openai_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = OpenAILLMConfig(
        meta=OpenAIMetaConfig(),
        provider=LLMProvider.OPENAI,
        http_client=OpenAIHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.openai.com/v1"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
