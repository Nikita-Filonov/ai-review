import json

import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from ai_review.clients.azure_openai.client import get_azure_openai_http_client, AzureOpenAIHTTPClient
from ai_review.clients.azure_openai.schema import AzureOpenAIChatRequestSchema, AzureOpenAIMessage
from ai_review.config import settings


@pytest.mark.usefixtures("azure_openai_http_client_config")
def test_get_azure_openai_http_client_builds_ok():
    azure_openai_http_client = get_azure_openai_http_client()

    assert isinstance(azure_openai_http_client, AzureOpenAIHTTPClient)
    assert isinstance(azure_openai_http_client.client, AsyncClient)


@pytest.mark.asyncio
@pytest.mark.usefixtures("azure_openai_http_client_config")
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
        client = AzureOpenAIHTTPClient(client=http_client)
        response = await client.chat(
            AzureOpenAIChatRequestSchema(messages=[AzureOpenAIMessage(role="user", content="Review this")]),
        )

    assert response.first_text == "answer"
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == f"/openai/deployments/{settings.llm.meta.model}/chat/completions"
    assert json.loads(requests[0].content) == {"messages": [{"role": "user", "content": "Review this"}]}
    assert requests[0].url.params["api-version"] == settings.llm.http_client.api_version
