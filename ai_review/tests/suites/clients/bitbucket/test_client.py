import pytest
from httpx import AsyncClient

from ai_review.clients.bitbucket.client import get_bitbucket_http_client, BitbucketHTTPClient
from ai_review.clients.bitbucket.pr.client import BitbucketPullRequestsHTTPClient


@pytest.mark.usefixtures("bitbucket_http_client_config")
def test_get_bitbucket_http_client_builds_ok():
    bitbucket_http_client = get_bitbucket_http_client()

    assert isinstance(bitbucket_http_client, BitbucketHTTPClient)
    assert isinstance(bitbucket_http_client.pr, BitbucketPullRequestsHTTPClient)
    assert isinstance(bitbucket_http_client.pr.client, AsyncClient)
