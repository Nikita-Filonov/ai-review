import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.openai.v2.client import get_openai_v2_http_client, OpenAIV2HTTPClient
from ai_review.clients.openai.v2.schema import OpenAIResponsesRequestSchema, OpenAIInputMessageSchema


@pytest.mark.usefixtures("openai_v2_http_client_config")
def test_get_openai_v2_http_client_builds_ok():
    openai_http_client = get_openai_v2_http_client()

    assert isinstance(openai_http_client, OpenAIV2HTTPClient)
    assert isinstance(openai_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v2_http_client_config")
async def test_chat_sends_request_and_parses_response() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(
            200,
            json={
                "usage": {"total_tokens": 2, "input_tokens": 1, "output_tokens": 1},
                "output": [{"type": "message", "content": [{"type": "output_text", "text": "answer"}]}],
            },
        )

    async with AsyncClient(
        base_url="https://example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = OpenAIV2HTTPClient(client=http_client)
        response = await client.chat(
            OpenAIResponsesRequestSchema(
                model="test-model", input=[OpenAIInputMessageSchema(role="user", content="Review this")]
            ),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/responses"
    assert json.loads(requests[0].content) == {
        "model": "test-model",
        "stream": False,
        "input": [{"role": "user", "content": "Review this"}],
    }
