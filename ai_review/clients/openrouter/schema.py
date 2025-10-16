from typing import Literal

from pydantic import BaseModel


class OpenRouterUsageSchema(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class OpenRouterMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class OpenRouterChoiceSchema(BaseModel):
    message: OpenRouterMessageSchema


class OpenRouterChatRequestSchema(BaseModel):
    model: str
    messages: list[OpenRouterMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class OpenRouterChatResponseSchema(BaseModel):
    usage: OpenRouterUsageSchema
    choices: list[OpenRouterChoiceSchema]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""
        return (self.choices[0].message.content or "").strip()
