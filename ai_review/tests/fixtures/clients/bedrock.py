from typing import Any

import pytest
from pydantic import HttpUrl

from ai_review.clients.bedrock.schema import (
    BedrockUsageSchema,
    BedrockContentSchema,
    BedrockChatRequestSchema,
    BedrockChatResponseSchema,
)
from ai_review.clients.bedrock.types import BedrockHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import BedrockLLMConfig
from ai_review.libs.config.llm.bedrock import BedrockMetaConfig, BedrockHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.bedrock.client import BedrockLLMClient


class FakeBedrockHTTPClient(BedrockHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: BedrockChatRequestSchema) -> BedrockChatResponseSchema:
        self.calls.append(("chat", {"request": request}))

        return self.responses.get(
            "chat",
            BedrockChatResponseSchema(
                id="fake-id",
                type="message",
                role="assistant",
                usage=BedrockUsageSchema(input_tokens=3, output_tokens=7),
                content=[
                    BedrockContentSchema(
                        type="text",
                        text="FAKE_BEDROCK_RESPONSE"
                    )
                ],
            ),
        )


@pytest.fixture
def fake_bedrock_http_client() -> FakeBedrockHTTPClient:
    return FakeBedrockHTTPClient()


@pytest.fixture
def bedrock_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_bedrock_http_client: FakeBedrockHTTPClient,
) -> BedrockLLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.bedrock.client.get_bedrock_http_client",
        lambda: fake_bedrock_http_client,
    )
    return BedrockLLMClient()


@pytest.fixture
def bedrock_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = BedrockLLMConfig(
        meta=BedrockMetaConfig(),
        provider=LLMProvider.BEDROCK,
        http_client=BedrockHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://bedrock-runtime.fake.aws"),
            region="us-east-1",
            access_key="FAKE_AWS_ACCESS_KEY",
            secret_key="FAKE_AWS_SECRET_KEY",
            session_token="FAKE_SESSION_TOKEN",
        ),
    )
    monkeypatch.setattr(settings, "llm", fake_config)
