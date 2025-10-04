from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class BitbucketPipelineConfig(BaseModel):
    workspace: str
    repo_slug: str
    pull_request_id: str


class BitbucketHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
