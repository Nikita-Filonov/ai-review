from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientConfig


class ClaudeMetaConfig(BaseModel):
    model: str = "claude-3-sonnet"
    max_tokens: int = 1200
    temperature: float = 0.3


class ClaudeHTTPClientConfig(HTTPClientConfig):
    api_version: str = "2023-06-01"
