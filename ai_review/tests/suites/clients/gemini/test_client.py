import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.gemini.client import get_gemini_http_client, GeminiHTTPClient
from ai_review.clients.gemini.schema import GeminiChatRequestSchema, GeminiContentSchema, GeminiPartSchema
from ai_review.config import settings


@pytest.mark.usefixtures("gemini_http_client_config")
def test_get_gemini_http_client_builds_ok():
    gemini_http_client = get_gemini_http_client()

    assert isinstance(gemini_http_client, GeminiHTTPClient)
    assert isinstance(gemini_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("gemini_http_client_config")
async def test_chat_sends_request_and_parses_response() -> None:
    requests: list[Request] = []

    def handler(request: Request) -> Response:
        requests.append(request)
        return Response(
            200,
            json={
                "usageMetadata": {"promptTokenCount": 1},
                "candidates": [{"content": {"parts": [{"text": "answer"}]}}],
            },
        )

    async with AsyncClient(
        base_url="https://example.test",
        transport=MockTransport(handler),
    ) as http_client:
        client = GeminiHTTPClient(client=http_client)
        response = await client.chat(
            GeminiChatRequestSchema(
                contents=[GeminiContentSchema(parts=[GeminiPartSchema(text="Review this")])]
            ),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == f"/v1beta/models/{settings.llm.meta.model}:generateContent"
    assert json.loads(requests[0].content) == {
        "contents": [{"role": "user", "parts": [{"text": "Review this"}]}]
    }
