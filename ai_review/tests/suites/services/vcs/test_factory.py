import pytest

from ai_review.services.vcs.bitbucket.client import BitbucketVCSClient
from ai_review.services.vcs.factory import get_vcs_client
from ai_review.services.vcs.gitea.client import GiteaVCSClient
from ai_review.services.vcs.github.client import GitHubVCSClient
from ai_review.services.vcs.gitlab.client import GitLabVCSClient


@pytest.mark.usefixtures("gitea_http_client_config")
def test_get_vcs_client_returns_gitea(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, GiteaVCSClient)


@pytest.mark.usefixtures("github_http_client_config")
def test_get_vcs_client_returns_github(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, GitHubVCSClient)


@pytest.mark.usefixtures("gitlab_http_client_config")
def test_get_vcs_client_returns_gitlab(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, GitLabVCSClient)


@pytest.mark.usefixtures("bitbucket_http_client_config")
def test_get_vcs_client_returns_bitbucket(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, BitbucketVCSClient)


def test_get_vcs_client_unsupported_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("ai_review.services.vcs.factory.settings.vcs.provider", "UNSUPPORTED")
    with pytest.raises(ValueError):
        get_vcs_client()
