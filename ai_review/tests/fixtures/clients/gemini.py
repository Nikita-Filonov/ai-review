import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.config import settings
from ai_review.libs.config.llm.base import GeminiLLMConfig
from ai_review.libs.config.llm.gemini import GeminiMetaConfig, GeminiHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


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
