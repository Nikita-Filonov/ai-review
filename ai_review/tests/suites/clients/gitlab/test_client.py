import pytest
from httpx import AsyncClient

from ai_review.clients.gitlab.client import get_gitlab_http_client, GitLabHTTPClient
from ai_review.clients.gitlab.mr.client import GitLabMergeRequestsHTTPClient


@pytest.mark.usefixtures("gitlab_http_client_config")
def test_get_gitlab_http_client_builds_ok():
    gitlab_http_client = get_gitlab_http_client()

    assert isinstance(gitlab_http_client, GitLabHTTPClient)
    assert isinstance(gitlab_http_client.mr, GitLabMergeRequestsHTTPClient)
    assert isinstance(gitlab_http_client.mr.client, AsyncClient)
