import pytest
from httpx import AsyncClient
from pydantic import HttpUrl, SecretStr

from ai_review.clients.openai.client import get_openai_http_client, OpenAIHTTPClient
from ai_review.config import settings
from ai_review.libs.config.llm import OpenAILLMConfig
from ai_review.libs.config.openai import OpenAIMetaConfig, OpenAIHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


@pytest.fixture(autouse=True)
def openai_http_client_config(monkeypatch):
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


def test_get_openai_http_client_builds_ok():
    openai_http_client = get_openai_http_client()

    assert isinstance(openai_http_client, OpenAIHTTPClient)
    assert isinstance(openai_http_client.client, AsyncClient)
