import pytest

from ai_review.clients.claude.schema import ClaudeChatResponseSchema
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("claude_http_client_config")
async def test_claude_llm_chat_uses_text_after_thinking_block(
        claude_llm_client: ClaudeLLMClient,
        fake_claude_http_client: FakeClaudeHTTPClient
) -> None:
    fake_claude_http_client.responses["chat"] = ClaudeChatResponseSchema.model_validate(
        {
            "id": "fake-id",
            "role": "assistant",
            "usage": {
                "input_tokens": 5,
                "output_tokens": 7,
            },
            "content": [
                {
                    "type": "thinking",
                    "thinking": "",
                    "signature": "fake-signature",
                },
                {
                    "type": "text",
                    "text": "FAKE_CLAUDE_SONNET_5_RESPONSE",
                },
            ],
        }
    )

    result = await claude_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_CLAUDE_SONNET_5_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7
