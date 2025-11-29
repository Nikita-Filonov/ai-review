from ai_review.libs.config.http import HTTPClientConfig
from ai_review.libs.config.llm.meta import LLMMetaConfig


class BedrockMetaConfig(LLMMetaConfig):
    model: str = "anthropic.claude-3-sonnet-20240229-v1:0"


class BedrockHTTPClientConfig(HTTPClientConfig):
    region: str = "us-east-1"
    access_key: str
    secret_key: str
    session_token: str | None = None
