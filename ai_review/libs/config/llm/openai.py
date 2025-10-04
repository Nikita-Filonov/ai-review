from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class OpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o-mini"


class OpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
