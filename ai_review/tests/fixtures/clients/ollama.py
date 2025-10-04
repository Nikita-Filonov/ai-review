import pytest
from pydantic import HttpUrl

from ai_review.config import settings
from ai_review.libs.config.llm.base import OllamaLLMConfig
from ai_review.libs.config.llm.ollama import OllamaMetaConfig, OllamaHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider


@pytest.fixture
def ollama_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = OllamaLLMConfig(
        meta=OllamaMetaConfig(),
        provider=LLMProvider.OLLAMA,
        http_client=OllamaHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("http://localhost:11434")
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
