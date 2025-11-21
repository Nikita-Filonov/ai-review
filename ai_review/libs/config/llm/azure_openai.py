from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class AzureOpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o-mini"


class AzureOpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    api_version: str = "2024-06-01"
