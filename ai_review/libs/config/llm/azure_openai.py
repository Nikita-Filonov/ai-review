from pydantic import Field, model_validator

from ai_review.libs.config.http import HTTPClientWithTokenConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class AzureOpenAIMetaConfig(LLMMetaConfig):
    model: str = "gpt-4o-mini"
    max_completion_tokens: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_token_limits_mutually_exclusive(self) -> "AzureOpenAIMetaConfig":
        if (self.max_tokens is not None) and (self.max_completion_tokens is not None):
            raise ValueError(
                "max_tokens and max_completion_tokens are mutually exclusive, set only one"
            )

        return self


class AzureOpenAIHTTPClientConfig(HTTPClientWithTokenConfig):
    api_version: str = "2024-06-01"
