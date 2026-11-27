import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.llmtr.client import get_llmtr_http_client, LLMTRHTTPClient
from ai_review.clients.llmtr.schema import LLMTRChatRequestSchema, LLMTRMessageSchema


@pytest.mark.usefixtures("llmtr_http_client_config")
def test_get_llmtr_http_client_builds_ok():
    llmtr_http_client = get_llmtr_http_client()

    assert isinstance(llmtr_http_client, LLMTRHTTPClient)
    assert isinstance(llmtr_http_client.client, AsyncClient)
    assert llmtr_http_client.client.headers["Authorization"] == "Bearer fake-token"
    assert str(llmtr_http_client.client.base_url).rstrip("/") == "https://llmtr.com/v1"


@pytest.mark.asyncio
@pytest.mark.usefixtures("llmtr_http_client_config")
async def test_chat_sends_request_and_parses_response() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(
            200,
            json={
                "usage": {"total_tokens": 2, "prompt_tokens": 1, "completion_tokens": 1},
                "choices": [{"message": {"role": "assistant", "content": "answer"}}],
            },
        )

    async with AsyncClient(
        base_url="https://example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = LLMTRHTTPClient(client=http_client)
        response = await client.chat(
            LLMTRChatRequestSchema(
                model="test-model", messages=[LLMTRMessageSchema(role="user", content="Review this")]
            ),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/chat/completions"
    assert json.loads(requests[0].content) == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "Review this"}],
    }
