import pytest
from httpx import AsyncClient

from ai_review.clients.github.client import get_github_http_client, GitHubHTTPClient
from ai_review.clients.github.pr.client import GitHubPullRequestsHTTPClient


@pytest.mark.usefixtures("github_http_client_config")
def test_get_github_http_client_builds_ok():
    github_http_client = get_github_http_client()

    assert isinstance(github_http_client, GitHubHTTPClient)
    assert isinstance(github_http_client.pr, GitHubPullRequestsHTTPClient)
    assert isinstance(github_http_client.pr.client, AsyncClient)
