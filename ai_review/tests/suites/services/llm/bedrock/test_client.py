import pytest

from ai_review.services.llm.claude.client import ClaudeLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.claude import FakeClaudeHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bedrock_http_client_config")
async def test_bedrock_llm_chat(
        bedrock_llm_client: ClaudeLLMClient,
        fake_bedrock_http_client: FakeClaudeHTTPClient
):
    result = await bedrock_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_BEDROCK_RESPONSE"
    assert result.total_tokens == 10
    assert result.prompt_tokens == 3
    assert result.completion_tokens == 7

    assert fake_bedrock_http_client.calls[0][0] == "chat"
