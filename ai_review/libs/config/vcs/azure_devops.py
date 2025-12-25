from enum import StrEnum

from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class AzureDevOpsTokenType(StrEnum):
    PAT = "PAT"
    OAUTH2 = "OAUTH2"


class AzureDevOpsPipelineConfig(BaseModel):
    organization: str
    project: str
    repository_id: str
    pull_request_id: int
    iteration_id: int


class AzureDevOpsHTTPClientConfig(HTTPClientWithTokenConfig):
    api_version: str = "7.0"
    api_token_type: AzureDevOpsTokenType = AzureDevOpsTokenType.OAUTH2
