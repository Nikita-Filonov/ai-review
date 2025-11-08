import pytest
from httpx import AsyncClient

from ai_review.clients.bitbucket_server.client import get_bitbucket_server_http_client, BitbucketServerHTTPClient
from ai_review.clients.bitbucket_server.pr.client import BitbucketServerPullRequestsHTTPClient


@pytest.mark.usefixtures("bitbucket_server_http_client_config")
def test_get_bitbucket_server_http_client_builds_ok():
    bitbucket_server_http_client = get_bitbucket_server_http_client()

    assert isinstance(bitbucket_server_http_client, BitbucketServerHTTPClient)
    assert isinstance(bitbucket_server_http_client.pr, BitbucketServerPullRequestsHTTPClient)
    assert isinstance(bitbucket_server_http_client.pr.client, AsyncClient)
