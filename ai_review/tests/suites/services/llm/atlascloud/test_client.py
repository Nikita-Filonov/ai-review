import pytest

from ai_review.services.llm.atlascloud.client import AtlasCloudLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.atlascloud import FakeAtlasCloudHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("atlascloud_http_client_config")
async def test_atlascloud_llm_chat(
        atlascloud_llm_client: AtlasCloudLLMClient,
        fake_atlascloud_http_client: FakeAtlasCloudHTTPClient
):
    result = await atlascloud_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_ATLASCLOUD_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_atlascloud_http_client.calls[0][0] == "chat"
