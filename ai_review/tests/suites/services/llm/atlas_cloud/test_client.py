import pytest
from pydantic import SecretStr

from ai_review.config import settings
from ai_review.libs.config.llm.atlas_cloud import (
    AtlasCloudHTTPClientConfig,
    AtlasCloudMetaConfig,
)
from ai_review.libs.config.llm.base import AtlasCloudLLMConfig
from ai_review.libs.constants.llm_provider import LLMProvider
from ai_review.services.llm.atlas_cloud.client import AtlasCloudLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.openai import FakeOpenAIV1HTTPClient


@pytest.mark.asyncio
async def test_atlas_cloud_llm_chat(monkeypatch: pytest.MonkeyPatch):
    fake_http_client = FakeOpenAIV1HTTPClient()
    config = AtlasCloudLLMConfig(
        provider=LLMProvider.ATLAS_CLOUD,
        meta=AtlasCloudMetaConfig(max_tokens=1200, temperature=0.3),
        http_client=AtlasCloudHTTPClientConfig(api_token=SecretStr("fake-token")),
    )
    monkeypatch.setattr(settings, "llm", config)
    monkeypatch.setattr(
        "ai_review.services.llm.atlas_cloud.client.get_openai_v1_http_client",
        lambda: fake_http_client,
    )

    result = await AtlasCloudLLMClient().chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OPENAI_V1_RESPONSE"
    request = fake_http_client.calls[0][1]["request"]
    assert request.model == "qwen/qwen3.8-max"
    assert [message.role for message in request.messages] == ["system", "user"]
