import pytest

from ai_review.clients.openrouter.schema import OpenRouterChatResponseSchema
from ai_review.services.llm.openrouter.client import OpenRouterLLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.openrouter import FakeOpenRouterHTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("openrouter_http_client_config")
async def test_openrouter_llm_chat(
        openrouter_llm_client: OpenRouterLLMClient,
        fake_openrouter_http_client: FakeOpenRouterHTTPClient
):
    result = await openrouter_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OPENROUTER_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_openrouter_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("openrouter_http_client_config")
async def test_chat_preserves_openrouter_first_choice(
        openrouter_llm_client: OpenRouterLLMClient,
        fake_openrouter_http_client: FakeOpenRouterHTTPClient,
) -> None:
    fake_openrouter_http_client.responses["chat"] = OpenRouterChatResponseSchema.model_validate({
        "usage": {"total_tokens": 30, "prompt_tokens": 10, "completion_tokens": 20},
        "choices": [
            {"message": {"role": "assistant", "content": " first "}},
            {"message": {"role": "assistant", "content": "second"}},
        ],
    })

    result = await openrouter_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == "first"
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20
