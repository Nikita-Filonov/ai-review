from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.gemini.schema import (
    GeminiPartSchema,
    GeminiUsageSchema,
    GeminiContentSchema,
    GeminiCandidateSchema,
    GeminiChatRequestSchema,
    GeminiChatResponseSchema,
)
from ai_review.clients.gemini.types import GeminiHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import GeminiLLMConfig
from ai_review.libs.config.llm.gemini import GeminiMetaConfig, GeminiHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.gemini.client import GeminiLLMClient


class FakeGeminiHTTPClient(GeminiHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: GeminiChatRequestSchema) -> GeminiChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            GeminiChatResponseSchema(
                usage=GeminiUsageSchema(prompt_token_count=2, total_tokens_count=10),
                candidates=[
                    GeminiCandidateSchema(
                        content=GeminiContentSchema(
                            role="model",
                            parts=[GeminiPartSchema(text="FAKE_GEMINI_RESPONSE")]
                        )
                    )
                ],
            ),
        )


@pytest.fixture
def fake_gemini_http_client() -> FakeGeminiHTTPClient:
    return FakeGeminiHTTPClient()


@pytest.fixture
def gemini_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_gemini_http_client: FakeGeminiHTTPClient
) -> GeminiLLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.gemini.client.get_gemini_http_client",
        lambda: fake_gemini_http_client,
    )
    return GeminiLLMClient()


@pytest.fixture
def gemini_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GeminiLLMConfig(
        meta=GeminiMetaConfig(),
        provider=LLMProvider.GEMINI,
        http_client=GeminiHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://generativelanguage.googleapis.com"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
