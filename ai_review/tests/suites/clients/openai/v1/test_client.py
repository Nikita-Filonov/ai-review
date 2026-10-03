import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.openai.v1.client import get_openai_v1_http_client, OpenAIV1HTTPClient
from ai_review.clients.openai.v1.schema import OpenAIChatRequestSchema, OpenAIMessageSchema


@pytest.mark.usefixtures("openai_v1_http_client_config")
def test_get_openai_v1_http_client_builds_ok():
    openai_http_client = get_openai_v1_http_client()

    assert isinstance(openai_http_client, OpenAIV1HTTPClient)
    assert isinstance(openai_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("openai_v1_http_client_config")
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
        client = OpenAIV1HTTPClient(client=http_client)
        response = await client.chat(
            OpenAIChatRequestSchema(
                model="test-model", messages=[OpenAIMessageSchema(role="user", content="Review this")]
            ),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/chat/completions"
    assert json.loads(requests[0].content) == {
        "model": "test-model",
        "stream": False,
        "messages": [{"role": "user", "content": "Review this"}],
    }
