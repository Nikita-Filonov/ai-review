from enum import StrEnum

from pydantic import BaseModel, Field

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class AzureDevOpsTokenType(StrEnum):
    OAUTH2 = "OAUTH2"
    PAT = "PAT"


class AzureDevOpsPipelineConfig(BaseModel):
    organization: str
    project: str
    repository_id: str
    pull_request_id: int
    iteration_id: int


class AzureDevOpsHTTPClientConfig(HTTPClientWithTokenConfig):
    api_version: str = "7.0"
    api_token_type: AzureDevOpsTokenType = Field(
        default=AzureDevOpsTokenType.OAUTH2
    )
