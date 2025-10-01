import pytest
from httpx import AsyncClient

from ai_review.clients.gemini.client import get_gemini_http_client, GeminiHTTPClient


@pytest.mark.usefixtures('gemini_http_client_config')
def test_get_gemini_http_client_builds_ok():
    gemini_http_client = get_gemini_http_client()

    assert isinstance(gemini_http_client, GeminiHTTPClient)
    assert isinstance(gemini_http_client.client, AsyncClient)
