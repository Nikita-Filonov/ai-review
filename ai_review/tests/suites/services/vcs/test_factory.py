import pytest

from ai_review.services.vcs.azure_devops.client import AzureDevOpsVCSClient
from ai_review.services.vcs.bitbucket_cloud.client import BitbucketCloudVCSClient
from ai_review.services.vcs.bitbucket_server.client import BitbucketServerVCSClient
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


@pytest.mark.usefixtures("azure_devops_http_client_config")
def test_get_vcs_client_returns_azure_devops(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, AzureDevOpsVCSClient)


@pytest.mark.usefixtures("bitbucket_cloud_http_client_config")
def test_get_vcs_client_returns_bitbucket_cloud(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, BitbucketCloudVCSClient)


@pytest.mark.usefixtures("bitbucket_server_http_client_config")
def test_get_vcs_client_returns_bitbucket_server(monkeypatch: pytest.MonkeyPatch):
    client = get_vcs_client()
    assert isinstance(client, BitbucketServerVCSClient)


def test_get_vcs_client_unsupported_provider(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("ai_review.services.vcs.factory.settings.vcs.provider", "UNSUPPORTED")
    with pytest.raises(ValueError):
        get_vcs_client()
