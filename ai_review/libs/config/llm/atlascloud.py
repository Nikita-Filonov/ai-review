from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class AtlasCloudMetaConfig(LLMMetaConfig):
    model: str = "deepseek-ai/deepseek-v4-pro"
    title: str | None = None
    referer: str | None = None


class AtlasCloudHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
