from typing import Any

import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.clients.atlascloud.schema import (
    AtlasCloudUsageSchema,
    AtlasCloudChoiceSchema,
    AtlasCloudMessageSchema,
    AtlasCloudChatRequestSchema,
    AtlasCloudChatResponseSchema,
)
from ai_review.clients.atlascloud.types import AtlasCloudHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.config.llm.base import AtlasCloudLLMConfig
from ai_review.libs.config.llm.atlascloud import AtlasCloudMetaConfig, AtlasCloudHTTPClientConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.atlascloud.client import AtlasCloudLLMClient


class FakeAtlasCloudHTTPClient(AtlasCloudHTTPClientProtocol):
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.responses = responses or {}

    async def chat(self, request: AtlasCloudChatRequestSchema) -> AtlasCloudChatResponseSchema:
        self.calls.append(("chat", {"request": request}))
        return self.responses.get(
            "chat",
            AtlasCloudChatResponseSchema(
                usage=AtlasCloudUsageSchema(total_tokens=12, prompt_tokens=5, completion_tokens=7),
                choices=[
                    AtlasCloudChoiceSchema(
                        message=AtlasCloudMessageSchema(
                            role="assistant",
                            content="FAKE_ATLASCLOUD_RESPONSE"
                        )
                    )
                ],
            ),
        )


@pytest.fixture
def fake_atlascloud_http_client() -> FakeAtlasCloudHTTPClient:
    return FakeAtlasCloudHTTPClient()


@pytest.fixture
def atlascloud_llm_client(
        monkeypatch: pytest.MonkeyPatch,
        fake_atlascloud_http_client: FakeAtlasCloudHTTPClient
) -> AtlasCloudLLMClient:
    monkeypatch.setattr(
        "ai_review.services.llm.atlascloud.client.get_atlascloud_http_client",
        lambda: fake_atlascloud_http_client,
    )
    return AtlasCloudLLMClient()


@pytest.fixture
def atlascloud_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = AtlasCloudLLMConfig(
        meta=AtlasCloudMetaConfig(),
        provider=LLMProvider.ATLASCLOUD,
        http_client=AtlasCloudHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://api.atlascloud.ai/v1"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "llm", fake_config)
