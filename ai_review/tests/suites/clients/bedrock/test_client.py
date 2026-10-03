from urllib.parse import quote

import httpx
import pytest
from httpx import AsyncClient

from ai_review.clients.bedrock.client import get_bedrock_http_client, BedrockHTTPClient
from ai_review.clients.bedrock.schema import BedrockChatRequestSchema
from ai_review.config import settings


@pytest.mark.usefixtures("bedrock_http_client_config")
def test_get_bedrock_http_client_builds_ok():
    bedrock_http_client = get_bedrock_http_client()

    assert isinstance(bedrock_http_client, BedrockHTTPClient)
    assert isinstance(bedrock_http_client.client, AsyncClient)


@pytest.mark.asyncio
async def test_bedrock_chat_signs_exact_body_and_parses_response(
    monkeypatch: pytest.MonkeyPatch,
    bedrock_http_client_config: None,
) -> None:
    signed: list[dict] = []

    def sign(**kwargs: object) -> dict[str, str]:
        signed.append(kwargs)
        return {"authorization": "signed"}

    monkeypatch.setattr("ai_review.clients.bedrock.client.sign_aws_v4", sign)

    def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "signed"
        assert request.content.decode() == signed[0]["body"]
        return httpx.Response(
            200,
            json={
                "id": "1",
                "type": "message",
                "role": "assistant",
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "content": [{"type": "text", "text": "answer"}],
            },
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond), base_url="https://example.test"
    ) as http_client:
        result = await BedrockHTTPClient(client=http_client).chat(
            BedrockChatRequestSchema(messages=[]),
        )

    assert result.first_text == "answer"
    assert signed[0]["method"] == "POST"
    assert signed[0]["url"].endswith(f"/model/{quote(settings.llm.meta.model, safe='-._~/')}/invoke")
