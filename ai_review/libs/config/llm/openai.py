from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class OpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o-mini"

    @property
    def is_v2_model(self) -> bool:
        return any(self.model.startswith(model) for model in ("gpt-5", "gpt-4.1"))


class OpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    pass
