import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.openrouter.client import get_openrouter_http_client, OpenRouterHTTPClient
from ai_review.clients.openrouter.schema import OpenRouterChatRequestSchema, OpenRouterMessageSchema
from ai_review.config import settings


@pytest.mark.usefixtures("openrouter_http_client_config")
def test_get_openrouter_http_client_builds_ok():
    openrouter_http_client = get_openrouter_http_client()

    assert isinstance(openrouter_http_client, OpenRouterHTTPClient)
    assert isinstance(openrouter_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("openrouter_http_client_config")
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
        client = OpenRouterHTTPClient(client=http_client)
        response = await client.chat(
            OpenRouterChatRequestSchema(
                model="test-model", messages=[OpenRouterMessageSchema(role="user", content="Review this")]
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


@pytest.mark.usefixtures("openrouter_http_client_config")
def test_openrouter_factory_includes_optional_attribution_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings.llm.meta, "title", "AI Review")
    monkeypatch.setattr(settings.llm.meta, "referer", "https://example.test")
    client = get_openrouter_http_client()
    assert client.client.headers["X-Title"] == "AI Review"
    assert client.client.headers["Referer"] == "https://example.test"
