from typing import Any
from pydantic import BaseModel, SecretStr, model_validator

from ai_review.libs.config.http import HTTPClientWithTokenConfig


class GitLabPipelineConfig(BaseModel):
    project_id: str
    merge_request_id: str


class GitLabHTTPClientConfig(HTTPClientWithTokenConfig):
    api_token: SecretStr = SecretStr("")
    job_token: SecretStr = SecretStr("")

    @property
    def job_token_value(self) -> str:
        return self.job_token.get_secret_value()

    @model_validator(mode="before")
    @classmethod
    def _validate_tokens(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not any([values.get("api_token"), values.get("job_token")]):
            raise ValueError(
                "Either 'api_token' or 'job_token' must be provided (can not both be empty)."
            )

        return values
