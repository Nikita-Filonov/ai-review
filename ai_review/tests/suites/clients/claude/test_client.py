import pytest
from httpx import AsyncClient

from ai_review.clients.claude.client import get_claude_http_client, ClaudeHTTPClient


@pytest.mark.usefixtures('claude_http_client_config')
def test_get_claude_http_client_builds_ok():
    claude_http_client = get_claude_http_client()

    assert isinstance(claude_http_client, ClaudeHTTPClient)
    assert isinstance(claude_http_client.client, AsyncClient)
