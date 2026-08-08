import pytest

from ai_review.libs.config.llm.openai import OpenAIReasoningConfig
from ai_review.services.llm.openai.client import OpenAILLMClient
from ai_review.services.llm.types import ChatResultSchema
from ai_review.tests.fixtures.clients.openai import FakeOpenAIV1HTTPClient, FakeOpenAIV2HTTPClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v1_http_client_config")
async def test_openai_llm_chat_v1(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v1_http_client: FakeOpenAIV1HTTPClient
):
    result = await openai_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OPENAI_V1_RESPONSE"
    assert result.total_tokens == 12
    assert result.prompt_tokens == 5
    assert result.completion_tokens == 7

    assert fake_openai_v1_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v1_http_client_config")
async def test_openai_llm_chat_v1_does_not_forward_reasoning_object(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v1_http_client: FakeOpenAIV1HTTPClient,
):
    openai_llm_client.meta.reasoning = OpenAIReasoningConfig(effort="medium")

    await openai_llm_client.chat("prompt", "prompt_system")

    request = fake_openai_v1_http_client.calls[0][1]["request"]
    assert "reasoning" not in request.model_dump(exclude_none=True)


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
async def test_openai_llm_chat_v2(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient
):
    result = await openai_llm_client.chat("prompt", "prompt_system")

    assert isinstance(result, ChatResultSchema)
    assert result.text == "FAKE_OPENAI_V2_RESPONSE"
    assert result.total_tokens == 20
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 10

    assert fake_openai_v2_http_client.calls[0][0] == "chat"


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
async def test_openai_llm_chat_v2_forwards_reasoning_object(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient,
):
    openai_llm_client.meta.reasoning = OpenAIReasoningConfig(
        effort="medium",
        summary="concise",
        context="all_turns",
        mode="pro",
        generate_summary="detailed",
    )

    await openai_llm_client.chat("prompt", "prompt_system")

    request = fake_openai_v2_http_client.calls[0][1]["request"]
    assert request.reasoning is not None
    assert request.reasoning.model_dump(exclude_none=True) == {
        "effort": "medium",
        "summary": "concise",
        "context": "all_turns",
        "mode": "pro",
        "generate_summary": "detailed",
    }
