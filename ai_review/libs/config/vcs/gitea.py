from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class GiteaPipelineConfig(BaseModel):
    repo: str
    owner: str
    pull_number: str


class GiteaHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
