from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ai_review.libs.config.vcs.bitbucket import BitbucketPipelineConfig, BitbucketHTTPClientConfig
from ai_review.libs.config.vcs.gitea import GiteaPipelineConfig, GiteaHTTPClientConfig
from ai_review.libs.config.vcs.github import GitHubPipelineConfig, GitHubHTTPClientConfig
from ai_review.libs.config.vcs.gitlab import GitLabPipelineConfig, GitLabHTTPClientConfig
from ai_review.libs.config.vcs.pagination import VCSPaginationConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


class VCSConfigBase(BaseModel):
    provider: VCSProvider
    pagination: VCSPaginationConfig = VCSPaginationConfig()


class GiteaVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITEA]
    pipeline: GiteaPipelineConfig
    http_client: GiteaHTTPClientConfig


class GitLabVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITLAB]
    pipeline: GitLabPipelineConfig
    http_client: GitLabHTTPClientConfig


class GitHubVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITHUB]
    pipeline: GitHubPipelineConfig
    http_client: GitHubHTTPClientConfig


class BitbucketVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.BITBUCKET]
    pipeline: BitbucketPipelineConfig
    http_client: BitbucketHTTPClientConfig


VCSConfig = Annotated[
    GiteaVCSConfig | GitLabVCSConfig | GitHubVCSConfig | BitbucketVCSConfig,
    Field(discriminator="provider")
]
