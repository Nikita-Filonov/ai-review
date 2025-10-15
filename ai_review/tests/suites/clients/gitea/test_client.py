import pytest
from httpx import AsyncClient

from ai_review.clients.gitea.client import get_gitea_http_client, GiteaHTTPClient
from ai_review.clients.gitea.pr.client import GiteaPullRequestsHTTPClient


@pytest.mark.usefixtures("gitea_http_client_config")
def test_get_gitea_http_client_builds_ok():
    gitea_http_client = get_gitea_http_client()

    assert isinstance(gitea_http_client, GiteaHTTPClient)
    assert isinstance(gitea_http_client.pr, GiteaPullRequestsHTTPClient)
    assert isinstance(gitea_http_client.pr.client, AsyncClient)
