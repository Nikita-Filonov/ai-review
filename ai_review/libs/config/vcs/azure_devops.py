from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class AzureDevOpsPipelineConfig(BaseModel):
    organization: str
    project: str
    repository_id: str
    pull_request_id: int
    iteration_id: int


class AzureDevOpsHTTPClientConfig(HTTPClientWithTokenConfig):
    api_version: str = "7.0"
