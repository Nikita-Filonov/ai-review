import pytest
from httpx import AsyncClient
from pydantic import HttpUrl, SecretStr

from ai_review.clients.github.client import get_github_http_client, GitHubHTTPClient
from ai_review.clients.github.pr.client import GitHubPullRequestsHTTPClient
from ai_review.config import settings
from ai_review.libs.config.github import GitHubPipelineConfig, GitHubHTTPClientConfig
from ai_review.libs.config.vcs import GitHubVCSConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


@pytest.fixture(autouse=True)
def github_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GitHubVCSConfig(
        provider=VCSProvider.GITHUB,
        pipeline=GitHubPipelineConfig(
            repo="repo",
            owner="owner",
            pull_number="pull_number"
        ),
        http_client=GitHubHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://github.com"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)


def test_get_github_http_client_builds_ok():
    github_http_client = get_github_http_client()

    assert isinstance(github_http_client, GitHubHTTPClient)
    assert isinstance(github_http_client.pr, GitHubPullRequestsHTTPClient)
    assert isinstance(github_http_client.pr.client, AsyncClient)
