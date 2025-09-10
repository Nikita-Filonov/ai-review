from pydantic_settings import BaseSettings, SettingsConfigDict

from libs.config.gitlab import GitLabHTTPClientConfig, GitLabPipelineConfig
from libs.config.openai import OpenAIHTTPClientConfig
from libs.config.prompt import PromptConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    prompt: PromptConfig
    gitlab_pipeline: GitLabPipelineConfig
    gitlab_http_client: GitLabHTTPClientConfig
    openai_http_client: OpenAIHTTPClientConfig


settings = Settings()
