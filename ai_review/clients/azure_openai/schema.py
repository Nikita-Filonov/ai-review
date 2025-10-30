from typing import Literal
from pydantic import BaseModel


class AzureOpenAIUsageSchema(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class AzureOpenAIMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AzureOpenAIChoiceSchema(BaseModel):
    message: AzureOpenAIMessageSchema


class AzureOpenAIChatRequestSchema(BaseModel):
    messages: list[AzureOpenAIMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class AzureOpenAIChatResponseSchema(BaseModel):
    usage: AzureOpenAIUsageSchema
    choices: list[AzureOpenAIChoiceSchema]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""
        return (self.choices[0].message.content or "").strip()

