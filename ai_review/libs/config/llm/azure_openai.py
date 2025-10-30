from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class AzureOpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o"
    api_version: str = "2024-08-01-preview"
    deployment_name: str = ""  # Azure deployment name


class AzureOpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    pass

