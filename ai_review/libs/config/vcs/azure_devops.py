from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class AzureDevOpsPipelineConfig(BaseModel):
    organization: str
    project: str
    repository_id: str  # Can be GUID or repository name
    pull_request_id: str


class AzureDevOpsHTTPClientConfig(HTTPClientWithTokenConfig):
    pass

