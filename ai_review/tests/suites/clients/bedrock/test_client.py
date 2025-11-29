import pytest
from httpx import AsyncClient

from ai_review.clients.bedrock.client import get_bedrock_http_client, BedrockHTTPClient


@pytest.mark.usefixtures('bedrock_http_client_config')
def test_get_bedrock_http_client_builds_ok():
    bedrock_http_client = get_bedrock_http_client()

    assert isinstance(bedrock_http_client, BedrockHTTPClient)
    assert isinstance(bedrock_http_client.client, AsyncClient)
