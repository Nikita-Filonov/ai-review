import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.config import settings
from ai_review.libs.config.llm.base import OpenAILLMConfig
from ai_review.libs.config.llm.openai import OpenAIMetaConfig, OpenAIHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


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
