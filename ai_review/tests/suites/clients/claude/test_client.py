import pytest
from httpx import AsyncClient
from pydantic import HttpUrl, SecretStr

from ai_review.clients.claude.client import get_claude_http_client, ClaudeHTTPClient
from ai_review.config import settings
from ai_review.libs.config.claude import ClaudeMetaConfig
from ai_review.libs.config.llm import ClaudeLLMConfig, ClaudeHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


@pytest.fixture(autouse=True)
def claude_http_client_config(monkeypatch):
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


def test_get_claude_http_client_builds_ok():
    claude_http_client = get_claude_http_client()

    assert isinstance(claude_http_client, ClaudeHTTPClient)
    assert isinstance(claude_http_client.client, AsyncClient)
