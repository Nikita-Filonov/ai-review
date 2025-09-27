from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientConfig


class GitHubPipelineConfig(BaseModel):
    repo: str
    owner: str
    pull_number: str


class GitHubHTTPClientConfig(HTTPClientConfig):
    pass
