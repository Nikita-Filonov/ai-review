import pytest
from httpx import AsyncClient

from ai_review.clients.atlascloud.client import get_atlascloud_http_client, AtlasCloudHTTPClient


@pytest.mark.usefixtures('atlascloud_http_client_config')
def test_get_atlascloud_http_client_builds_ok():
    atlascloud_http_client = get_atlascloud_http_client()

    assert isinstance(atlascloud_http_client, AtlasCloudHTTPClient)
    assert isinstance(atlascloud_http_client.client, AsyncClient)
