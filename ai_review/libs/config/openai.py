from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientConfig


class OpenAIMetaConfig(BaseModel):
    model: str = "gpt-4o-mini"
    max_tokens: int = 1200
    temperature: float = 0.3


class OpenAIHTTPClientConfig(HTTPClientConfig):
    pass
