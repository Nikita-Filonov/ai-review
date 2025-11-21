import pytest
from httpx import AsyncClient

from ai_review.clients.azure_openai.client import get_azure_openai_http_client, AzureOpenAIHTTPClient


@pytest.mark.usefixtures('azure_openai_http_client_config')
def test_get_azure_openai_http_client_builds_ok():
    azure_openai_http_client = get_azure_openai_http_client()

    assert isinstance(azure_openai_http_client, AzureOpenAIHTTPClient)
    assert isinstance(azure_openai_http_client.client, AsyncClient)
