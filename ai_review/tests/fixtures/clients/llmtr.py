from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.llmtr.schema import (
    LLMTRUsageSchema,
    LLMTRChoiceSchema,
    LLMTRMessageSchema,
    LLMTRChatRequestSchema,
    LLMTRChatResponseSchema,
)
from ai_review.clients.llmtr.types import LLMTRHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import LLMTRLLMConfig
from ai_review.libs.config.llm.llmtr import LLMTRMetaConfig, LLMTRHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.llmtr.client import LLMTRLLMClient


class FakeLLMTRHTTPClient(LLMTRHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: LLMTRChatRequestSchema) -> LLMTRChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            LLMTRChatResponseSchema(
                usage=LLMTRUsageSchema(total_tokens=12, prompt_tokens=5, completion_tokens=7),
                choices=[
                    LLMTRChoiceSchema(
                        message=LLMTRMessageSchema(
                            role="assistant",
                            content="FAKE_LLMTR_RESPONSE"
                        )
                    )
                ],
            ),
        )


@pytest.fixture
def fake_llmtr_http_client() -> FakeLLMTRHTTPClient:
    return FakeLLMTRHTTPClient()


@pytest.fixture
def llmtr_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_llmtr_http_client: FakeLLMTRHTTPClient
) -> LLMTRLLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.llmtr.client.get_llmtr_http_client",
        lambda: fake_llmtr_http_client,
    )
    return LLMTRLLMClient()


@pytest.fixture
def llmtr_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = LLMTRLLMConfig(
        meta=LLMTRMetaConfig(),
        provider=LLMProvider.LLMTR,
        http_client=LLMTRHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://llmtr.com/v1"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
