from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AzureOpenAITextBlock(BaseModel):
    type: Literal["text"]
    text: str


class AzureOpenAIMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str | list[AzureOpenAITextBlock]


class AzureOpenAIChoice(BaseModel):
    index: int | None = None
    finish_reason: str | None = None
    message: AzureOpenAIMessage


class AzureOpenAIUsage(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class AzureOpenAIChatQuerySchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    api_version: str = Field(alias="api-version")


class AzureOpenAIChatRequestSchema(BaseModel):
    messages: list[AzureOpenAIMessage]
    max_tokens: int | None = None
    temperature: float | None = None


class AzureOpenAIChatResponseSchema(BaseModel):
    usage: AzureOpenAIUsage
    choices: list[AzureOpenAIChoice]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""

        message = self.choices[0].message

        if isinstance(message.content, str):
            return message.content.strip()

        if isinstance(message.content, list):
            return "".join(block.text for block in message.content).strip()

        return ""
