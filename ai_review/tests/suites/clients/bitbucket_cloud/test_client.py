import pytest
from httpx import AsyncClient

from ai_review.clients.bitbucket_cloud.client import get_bitbucket_cloud_http_client, BitbucketCloudHTTPClient
from ai_review.clients.bitbucket_cloud.pr.client import BitbucketCloudPullRequestsHTTPClient


@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
def test_get_bitbucket_cloud_http_client_builds_ok():
    bitbucket_http_client = get_bitbucket_cloud_http_client()

    assert isinstance(bitbucket_http_client, BitbucketCloudHTTPClient)
    assert isinstance(bitbucket_http_client.pr, BitbucketCloudPullRequestsHTTPClient)
    assert isinstance(bitbucket_http_client.pr.client, AsyncClient)
