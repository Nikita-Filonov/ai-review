import pytest
from httpx import AsyncClient

from ai_review.clients.openrouter.client import get_openrouter_http_client, OpenRouterHTTPClient


@pytest.mark.usefixtures('openrouter_http_client_config')
def test_get_openrouter_http_client_builds_ok():
    openrouter_http_client = get_openrouter_http_client()

    assert isinstance(openrouter_http_client, OpenRouterHTTPClient)
    assert isinstance(openrouter_http_client.client, AsyncClient)
