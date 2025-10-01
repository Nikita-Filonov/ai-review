import pytest
from httpx import AsyncClient

from ai_review.clients.openai.client import get_openai_http_client, OpenAIHTTPClient


@pytest.mark.usefixtures('openai_http_client_config')
def test_get_openai_http_client_builds_ok():
    openai_http_client = get_openai_http_client()

    assert isinstance(openai_http_client, OpenAIHTTPClient)
    assert isinstance(openai_http_client.client, AsyncClient)
