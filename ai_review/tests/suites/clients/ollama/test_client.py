import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.ollama.client import get_ollama_http_client, OllamaHTTPClient
from ai_review.clients.ollama.schema import OllamaChatRequestSchema, OllamaMessageSchema


@pytest.mark.usefixtures("ollama_http_client_config")
def test_get_ollama_http_client_builds_ok():
    ollama_http_client = get_ollama_http_client()

    assert isinstance(ollama_http_client, OllamaHTTPClient)
    assert isinstance(ollama_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("ollama_http_client_config")
async def test_chat_sends_request_and_parses_response() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(
            200,
            json={"model": "test-model", "message": {"role": "assistant", "content": "answer"}},
        )

    async with AsyncClient(
        base_url="https://example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = OllamaHTTPClient(client=http_client)
        response = await client.chat(
            OllamaChatRequestSchema(
                model="test-model", messages=[OllamaMessageSchema(role="user", content="Review this")]
            ),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/api/chat"
    assert json.loads(requests[0].content) == {
        "model": "test-model",
        "stream": False,
        "messages": [{"role": "user", "content": "Review this"}],
    }
