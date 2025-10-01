import pytest
from pydantic import HttpUrl, SecretStr

from ai_review.config import settings
from ai_review.libs.config.gitlab import GitLabPipelineConfig, GitLabHTTPClientConfig
from ai_review.libs.config.vcs import GitLabVCSConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


@pytest.fixture
def gitlab_http_client_config(monkeypatch: pytest.MonkeyPatch):
    fake_config = GitLabVCSConfig(
        provider=VCSProvider.GITLAB,
        pipeline=GitLabPipelineConfig(
            project_id="project-id",
            merge_request_id="merge-request-id"
        ),
        http_client=GitLabHTTPClientConfig(
            timeout=10,
            api_url=HttpUrl("https://gitlab.com"),
            api_token=SecretStr("fake-token"),
        )
    )
    monkeypatch.setattr(settings, "vcs", fake_config)
