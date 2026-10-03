import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.claude.client import get_claude_http_client, ClaudeHTTPClient
from ai_review.clients.claude.schema import ClaudeChatRequestSchema, ClaudeMessageSchema


@pytest.mark.usefixtures('claude_http_client_config')
def test_get_claude_http_client_builds_ok():
    claude_http_client = get_claude_http_client()

    assert isinstance(claude_http_client, ClaudeHTTPClient)
    assert isinstance(claude_http_client.client, AsyncClient)


@pytest.mark.asyncio
async def test_chat_parses_response_with_thinking_block() -> None:
    requests: list[Request] = []

    async def handler(request: Request) -> Response:
        requests.append(request)
        return Response(
            status_code=200,
            request=request,
            json={
                "id": "msg_123",
                "role": "assistant",
                "usage": {
                    "input_tokens": 11,
                    "output_tokens": 13,
                },
                "content": [
                    {
                        "type": "thinking",
                        "thinking": "",
                        "signature": "fake-signature",
                    },
                    {
                        "type": "text",
                        "text": " review result ",
                    },
                ],
            },
        )

    async with AsyncClient(
            base_url="https://api.anthropic.com",
            transport=MockTransport(handler),
    ) as http_client:
        claude_http_client = ClaudeHTTPClient(client=http_client)
        response = await claude_http_client.chat(
            ClaudeChatRequestSchema(
                model="claude-sonnet-5",
                messages=[ClaudeMessageSchema(role="user", content="Review this")],
                max_tokens=1000,
            )
        )

    assert response.first_text == "review result"
    assert response.usage.total_tokens == 24
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/v1/messages"
    assert json.loads(requests[0].content) == {
        "model": "claude-sonnet-5",
        "messages": [
            {
                "role": "user",
                "content": "Review this",
            }
        ],
        "max_tokens": 1000,
    }
