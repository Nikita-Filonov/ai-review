from pydantic import Field

from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class OpenRouterMetaConfig(LLMMetaConfig):
    model: str = "openai/gpt-4o-mini"
    title: str | None = None
    referer: str | None = None
    max_tokens: int | None = Field(default=None, ge=1)


class OpenRouterHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
