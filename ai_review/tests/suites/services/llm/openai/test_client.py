import pytest

from ai_review.clients.openai.v1.schema import OpenAIChatResponseSchema
from ai_review.clients.openai.v2.schema import OpenAIResponsesResponseSchema
from ai_review.libs.config.llm.openai import OpenAIMetaConfig, OpenAIReasoningConfig
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
async def test_gpt_6_luna_uses_responses_without_temperature(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v1_http_client: FakeOpenAIV1HTTPClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient,
):
    openai_llm_client.meta = OpenAIMetaConfig(
        model="gpt-6-luna",
        max_tokens=15000,
        reasoning=OpenAIReasoningConfig(effort="medium"),
    )

    await openai_llm_client.chat("prompt", "system")

    assert fake_openai_v1_http_client.calls == []
    request = fake_openai_v2_http_client.calls[0][1]["request"]
    payload = request.model_dump(exclude_none=True)
    assert payload["model"] == "gpt-6-luna"
    assert payload["reasoning"] == {"effort": "medium"}
    assert payload["max_output_tokens"] == 15000
    assert "temperature" not in payload


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v1_http_client_config")
async def test_chat_preserves_openai_chat_first_choice(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v1_http_client: FakeOpenAIV1HTTPClient,
) -> None:
    fake_openai_v1_http_client.responses["chat"] = OpenAIChatResponseSchema.model_validate({
        "usage": {"total_tokens": 30, "prompt_tokens": 10, "completion_tokens": 20},
        "choices": [
            {"message": {"role": "assistant", "content": " first "}},
            {"message": {"role": "assistant", "content": "second"}},
        ],
    })

    result = await openai_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == "first"
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
async def test_chat_v2_preserves_json_split_across_content_blocks(
        openai_llm_client: OpenAILLMClient,
        fake_openai_v2_http_client: FakeOpenAIV2HTTPClient,
) -> None:
    fake_openai_v2_http_client.responses["chat"] = OpenAIResponsesResponseSchema.model_validate({
        "usage": {"total_tokens": 30, "input_tokens": 10, "output_tokens": 20},
        "output": [{"type": "message", "content": [
            {"type": "output_text", "text": '{"action":"TOOL_CALL",'},
            {"type": "output_text", "text": '"command":"ls"}'},
            {"type": "output_text", "text": '{"action":"TOOL_CALL","command":"cat a.py"}'},
        ]}],
    })

    result = await openai_llm_client.chat("PROMPT", "SYSTEM")

    assert result.text == '{"action":"TOOL_CALL","command":"ls"}{"action":"TOOL_CALL","command":"cat a.py"}'
    assert result.total_tokens == 30
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 20
