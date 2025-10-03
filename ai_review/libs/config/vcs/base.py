from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ai_review.libs.config.vcs.github import GitHubPipelineConfig, GitHubHTTPClientConfig
from ai_review.libs.config.vcs.gitlab import GitLabPipelineConfig, GitLabHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


class VCSConfigBase(BaseModel):
    provider: VCSProvider


class GitLabVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITLAB]
    pipeline: GitLabPipelineConfig
    http_client: GitLabHTTPClientConfig


class GitHubVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITHUB]
    pipeline: GitHubPipelineConfig
    http_client: GitHubHTTPClientConfig


VCSConfig = Annotated[GitLabVCSConfig | GitHubVCSConfig, Field(discriminator="provider")]
