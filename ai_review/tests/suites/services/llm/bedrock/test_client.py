import pytest

from ai_review.clients.bedrock.schema import BedrockChatResponseSchema
from ai_review.services.llm.bedrock.client import BedrockLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.bedrock import FakeBedrockHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("bedrock_http_client_config")
async def test_bedrock_llm_chat(
        bedrock_llm_client: BedrockLLMClient,
        fake_bedrock_http_client: FakeBedrockHTTPClient
):
    result = await bedrock_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_BEDROCK_RESPONSE"
    assert result.total_tokens == 10
    assert result.prompt_tokens == 3
    assert result.completion_tokens == 7

    assert fake_bedrock_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("bedrock_http_client_config")
async def test_chat_preserves_bedrock_first_block(
        bedrock_llm_client: BedrockLLMClient,
        fake_bedrock_http_client: FakeBedrockHTTPClient,
) -> None:
    fake_bedrock_http_client.responses["chat"] = BedrockChatResponseSchema.model_validate({
        "id": "test", "type": "message", "role": "assistant",
        "usage": {"input_tokens": 10, "output_tokens": 20},
        "content": [{"type": "text", "text": " first "}, {"type": "text", "text": "second"}],
    })

    result = await bedrock_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == "first"
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20
