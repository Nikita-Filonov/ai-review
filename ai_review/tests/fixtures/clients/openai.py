from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.openai.v1.schema import (
    OpenAIUsageSchema,
    OpenAIChoiceSchema,
    OpenAIMessageSchema,
    OpenAIChatRequestSchema,
    OpenAIChatResponseSchema,
)
from ai_review.clients.openai.v1.types import OpenAIV1HTTPClientProtocol
from ai_review.clients.openai.v2.schema import (
    OpenAIResponsesRequestSchema,
    OpenAIResponsesResponseSchema,
    OpenAIResponseUsageSchema,
    OpenAIResponseOutputSchema,
    OpenAIResponseContentSchema,
)
from ai_review.clients.openai.v2.types import OpenAIV2HTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import OpenAILLMConfig
from ai_review.libs.config.llm.openai import OpenAIMetaConfig, OpenAIHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.openai.client import OpenAILLMClient


class FakeOpenAIV1HTTPClient(OpenAIV1HTTPClientProtocol):
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
                        message=OpenAIMessageSchema(
                            role="assistant",
                            content="FAKE_OPENAI_V1_RESPONSE"
                        )
                    )
                ],
            ),
        )


class FakeOpenAIV2HTTPClient(OpenAIV2HTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: OpenAIResponsesRequestSchema) -> OpenAIResponsesResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            OpenAIResponsesResponseSchema(
                usage=OpenAIResponseUsageSchema(
                    total_tokens=20, input_tokens=10, output_tokens=10
                ),
                output=[
                    OpenAIResponseOutputSchema(
                        type="message",
                        role="assistant",
                        content=[
                            OpenAIResponseContentSchema(
                                type="output_text",
                                text="FAKE_OPENAI_V2_RESPONSE"
                            )
                        ],
                    )
                ],
            ),
        )


@pytest.fixture
def fake_openai_v1_http_client() -> FakeOpenAIV1HTTPClient:
    return FakeOpenAIV1HTTPClient()


@pytest.fixture
def fake_openai_v2_http_client() -> FakeOpenAIV2HTTPClient:
    return FakeOpenAIV2HTTPClient()


@pytest.fixture
def openai_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_openai_v1_http_client: FakeOpenAIV1HTTPClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient,
) -> OpenAILLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.openai.client.get_openai_v1_http_client",
        lambda: fake_openai_v1_http_client,
    )
    monkeypatch.setattr(
        "ai_review.services.llm.openai.client.get_openai_v2_http_client",
        lambda: fake_openai_v2_http_client,
    )
    return OpenAILLMClient()


@pytest.fixture
def openai_v1_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = OpenAILLMConfig(
        meta=OpenAIMetaConfig(
            model="gpt-4o-mini",
            max_tokens=1200,
            temperature=0.3
        ),
        provider=LLMProvider.OPENAI,
        http_client=OpenAIHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.openai.com/v1"),
            api_token=SecretStr("fake-token"),
        ),
    )
    monkeypatch.setattr(settings, "llm", fake_config)


@pytest.fixture
def openai_v2_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = OpenAILLMConfig(
        meta=OpenAIMetaConfig(
            model="gpt-5",
            max_tokens=2000,
            temperature=0.2
        ),
        provider=LLMProvider.OPENAI,
        http_client=OpenAIHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.openai.com/v1"),
            api_token=SecretStr("fake-token"),
        ),
    )
    monkeypatch.setattr(settings, "llm", fake_config)
