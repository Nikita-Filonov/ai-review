import pytest

from ai_review.clients.llmtr.schema import LLMTRChatResponseSchema
from ai_review.services.llm.llmtr.client import LLMTRLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.llmtr import FakeLLMTRHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("llmtr_http_client_config")
async def test_llmtr_llm_chat(
        llmtr_llm_client: LLMTRLLMClient,
        fake_llmtr_http_client: FakeLLMTRHTTPClient
):
    result = await llmtr_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_LLMTR_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_llmtr_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("llmtr_http_client_config")
async def test_chat_preserves_llmtr_first_choice(
        llmtr_llm_client: LLMTRLLMClient,
        fake_llmtr_http_client: FakeLLMTRHTTPClient,
) -> None:
    fake_llmtr_http_client.responses["chat"] = LLMTRChatResponseSchema.model_validate({
        "usage": {"total_tokens": 30, "prompt_tokens": 10, "completion_tokens": 20},
        "choices": [
            {"message": {"role": "assistant", "content": " first "}},
            {"message": {"role": "assistant", "content": "second"}},
        ],
    })

    result = await llmtr_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == "first"
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20
