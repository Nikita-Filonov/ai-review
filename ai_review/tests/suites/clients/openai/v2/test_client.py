import pytest
from httpx import AsyncClient

from ai_review.clients.openai.v2.client import get_openai_v2_http_client, OpenAIV2HTTPClient


@pytest.mark.usefixtures('openai_v2_http_client_config')
def test_get_openai_v2_http_client_builds_ok():
    openai_http_client = get_openai_v2_http_client()

    assert isinstance(openai_http_client, OpenAIV2HTTPClient)
    assert isinstance(openai_http_client.client, AsyncClient)
