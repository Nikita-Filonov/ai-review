from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.claude.schema import (
    ClaudeUsageSchema,
    ClaudeContentSchema,
    ClaudeChatRequestSchema,
    ClaudeChatResponseSchema,
)
from ai_review.clients.claude.types import ClaudeHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import ClaudeLLMConfig
from ai_review.libs.config.llm.claude import ClaudeMetaConfig, ClaudeHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.claude.client import ClaudeLLMClient


class FakeClaudeHTTPClient(ClaudeHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: ClaudeChatRequestSchema) -> ClaudeChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            ClaudeChatResponseSchema(
                id="fake-id",
                role="assistant",
                usage=ClaudeUsageSchema(input_tokens=5, output_tokens=7),
                content=[ClaudeContentSchema(type="text", text="FAKE_CLAUDE_RESPONSE")],
            ),
        )


@pytest.fixture
def fake_claude_http_client():
    return FakeClaudeHTTPClient()


@pytest.fixture
def claude_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_claude_http_client: FakeClaudeHTTPClient
) -> ClaudeLLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.claude.client.get_claude_http_client",
        lambda: fake_claude_http_client,
    )
    return ClaudeLLMClient()


@pytest.fixture
def claude_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = ClaudeLLMConfig(
        meta=ClaudeMetaConfig(),
        provider=LLMProvider.CLAUDE,
        http_client=ClaudeHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.anthropic.com"),
            api_token=SecretStr("fake-token"),
            api_version="2023-06-01",
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
