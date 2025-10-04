import pytest

from ai_review.services.llm.claude.client import ClaudeLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.claude import FakeClaudeHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("claude_http_client_config")
async def test_claude_llm_chat(
        claude_llm_client: ClaudeLLMClient,
        fake_claude_http_client: FakeClaudeHTTPClient
):
    result = await claude_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_CLAUDE_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_claude_http_client.calls[0][0] == "chat"
