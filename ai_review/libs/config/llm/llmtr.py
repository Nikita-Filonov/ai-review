from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class LLMTRMetaConfig(LLMMetaConfig):
    model: str = "qwen/qwen3.8-27b-free"


class LLMTRHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
