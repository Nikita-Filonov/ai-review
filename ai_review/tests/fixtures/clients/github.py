import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.config import settings
from ai_review.libs.config.github import GitHubPipelineConfig, GitHubHTTPClientConfig
from ai_review.libs.config.vcs import GitHubVCSConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


@pytest.fixture
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
