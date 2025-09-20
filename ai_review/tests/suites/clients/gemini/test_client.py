import pytest
from httpx import AsyncClient
from pydantic import HttpUrl, SecretStr

from ai_review.clients.gemini.client import get_gemini_http_client, GeminiHTTPClient
from ai_review.config import settings
from ai_review.libs.config.gemini import GeminiMetaConfig, GeminiHTTPClientConfig
from ai_review.libs.config.llm import GeminiLLMConfig
from ai_review.libs.constants.llm_provider import LLMProvider


@pytest.fixture(autouse=True)
def gemini_http_client_config(monkeypatch):
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


def test_get_gemini_http_client_builds_ok():
    gemini_http_client = get_gemini_http_client()

    assert isinstance(gemini_http_client, GeminiHTTPClient)
    assert isinstance(gemini_http_client.client, AsyncClient)
