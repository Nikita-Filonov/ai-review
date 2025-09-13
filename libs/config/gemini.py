from pydantic import BaseModel

from libs.config.http import HTTPClientConfig


class GeminiMetaConfig(BaseModel):
    model: str = "gemini-2.0-pro"
    temperature: float = 0.3
    max_output_tokens: int = 1200


class GeminiHTTPClientConfig(HTTPClientConfig):
    pass
