from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class GeminiMetaConfig(LLMMetaConfig):
    model: str = "gemini-2.0-pro"


class GeminiHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
