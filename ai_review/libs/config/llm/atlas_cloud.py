from pydantic import HttpUrl

from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class AtlasCloudMetaConfig(LLMMetaConfig):
    model: str = "qwen/qwen3.8-max"


class AtlasCloudHTTPClientConfig(HTTPClientWithTokenConfig):
    api_url: HttpUrl = HttpUrl("https://api.atlascloud.ai/v1")
