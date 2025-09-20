from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ai_review.libs.config.gitlab import GitLabPipelineConfig, GitLabHTTPClientConfig
from ai_review.libs.constants.vcs_provider import VCSProvider


class VCSConfigBase(BaseModel):
    provider: VCSProvider


class GitLabVCSConfig(VCSConfigBase):
    provider: Literal[VCSProvider.GITLAB]
    pipeline: GitLabPipelineConfig
    http_client: GitLabHTTPClientConfig


VCSConfig = Annotated[GitLabVCSConfig, Field(discriminator="provider")]
