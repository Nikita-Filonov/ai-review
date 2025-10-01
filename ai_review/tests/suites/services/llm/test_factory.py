import pytest

from ai_review.services.llm.claude.client import ClaudeLLMClient
from ai_review.services.llm.factory import get_llm_client
from ai_review.services.llm.gemini.client import GeminiLLMClient
from ai_review.services.llm.openai.client import OpenAILLMClient


@pytest.mark.usefixtures("openai_http_client_config")
def test_get_llm_client_returns_openai(monkeypatch: pytest.MonkeyPatch):
    client = get_llm_client()
    assert isinstance(client, OpenAILLMClient)


@pytest.mark.usefixtures("gemini_http_client_config")
def test_get_llm_client_returns_gemini(monkeypatch: pytest.MonkeyPatch):
    client = get_llm_client()
    assert isinstance(client, GeminiLLMClient)


@pytest.mark.usefixtures("claude_http_client_config")
def test_get_llm_client_returns_claude(monkeypatch: pytest.MonkeyPatch):
    client = get_llm_client()
    assert isinstance(client, ClaudeLLMClient)


def test_get_llm_client_unsupported_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("ai_review.services.llm.factory.settings.llm.provider", "DEEPSEEK")
    with pytest.raises(ValueError):
        get_llm_client()
