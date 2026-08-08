from pydantic import BaseModel

from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class OpenAIReasoningConfig(BaseModel):
    mode: str | None = None
    effort: str | None = None
    summary: str | None = None
    context: str | None = None
    generate_summary: str | None = None


class OpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o-mini"
    reasoning: OpenAIReasoningConfig | None = None

    @property
    def is_v2_model(self) -> bool:
        return any(self.model.startswith(model) for model in ("gpt-5", "gpt-4.1"))


class OpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
