from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class BitbucketCloudPipelineConfig(BaseModel):
    workspace: str
    repo_slug: str
    pull_request_id: str


class BitbucketCloudHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
