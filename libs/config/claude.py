from pydantic import BaseModel

from libs.config.http import HTTPClientConfig


class ClaudeMetaConfig(BaseModel):
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1200
    temperature: float = 0.3


class ClaudeHTTPClientConfig(HTTPClientConfig):
    pass
