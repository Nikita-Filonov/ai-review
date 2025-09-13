from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, Field, FilePath

from libs.config.claude import ClaudeHTTPClientConfig, ClaudeMetaConfig
from libs.config.gemini import GeminiHTTPClientConfig, GeminiMetaConfig
from libs.config.openai import OpenAIHTTPClientConfig, OpenAIMetaConfig
from libs.constants.llm_provider import LLMProvider


class LLMPricingConfig(BaseModel):
    input: float
    output: float


class LLMConfigBase(BaseModel):
    provider: LLMProvider
    pricing_file: FilePath = FilePath("./pricing.yaml")

    def load_pricing(self) -> dict[str, LLMPricingConfig]:
        data = self.pricing_file.read_text(encoding="utf-8")
        raw = yaml.safe_load(data)
        return {model: LLMPricingConfig(**values) for model, values in raw.items()}


class OpenAILLMConfig(LLMConfigBase):
    meta: OpenAIMetaConfig
    provider: Literal[LLMProvider.OPENAI]
    http_client: OpenAIHTTPClientConfig


class GeminiLLMConfig(LLMConfigBase):
    meta: GeminiMetaConfig
    provider: Literal[LLMProvider.GEMINI]
    http_client: GeminiHTTPClientConfig


class ClaudeLLMConfig(LLMConfigBase):
    meta: ClaudeMetaConfig
    provider: Literal[LLMProvider.CLAUDE]
    http_client: ClaudeHTTPClientConfig


LLMConfig = Annotated[
    OpenAILLMConfig | GeminiLLMConfig | ClaudeLLMConfig,
    Field(discriminator="provider")
]
