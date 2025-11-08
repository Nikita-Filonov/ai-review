from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ai_review.libs.config.vcs.azure_devops import AzureDevOpsPipelineConfig, AzureDevOpsHTTPClientConfig
from ai_review.libs.config.vcs.bitbucket_cloud import (
    BitbucketCloudPipelineConfig,
    BitbucketCloudHTTPClientConfig
)
from ai_review.libs.config.vcs.bitbucket_server import (
    BitbucketServerPipelineConfig,
    BitbucketServerHTTPClientConfig
)
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


class AzureDevOpsVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.AZURE_DEVOPS]
    pipeline: AzureDevOpsPipelineConfig
    http_client: AzureDevOpsHTTPClientConfig


class BitbucketCloudVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.BITBUCKET_CLOUD]
    pipeline: BitbucketCloudPipelineConfig
    http_client: BitbucketCloudHTTPClientConfig


class BitbucketServerVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.BITBUCKET_SERVER]
    pipeline: BitbucketServerPipelineConfig
    http_client: BitbucketServerHTTPClientConfig


VCSConfig = Annotated[
    GiteaVCSConfig
    | GitLabVCSConfig
    | GitHubVCSConfig
    | AzureDevOpsVCSConfig
    | BitbucketCloudVCSConfig
    | BitbucketServerVCSConfig,
    Field(discriminator="provider")
]
