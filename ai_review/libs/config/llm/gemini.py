from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientConfig


class GeminiMetaConfig(BaseModel):
    model: str = "gemini-2.0-pro"
    max_tokens: int = 1200
    temperature: float = 0.3


class GeminiHTTPClientConfig(HTTPClientConfig):
    pass
