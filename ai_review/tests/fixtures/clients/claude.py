import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.config import settings
from ai_review.libs.config.llm.base import ClaudeLLMConfig
from ai_review.libs.config.llm.claude import ClaudeMetaConfig, ClaudeHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


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
