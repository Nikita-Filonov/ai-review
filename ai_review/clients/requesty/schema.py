from typing import Literal

from pydantic import BaseModel


class RequestyUsageSchema(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class RequestyMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class RequestyChoiceSchema(BaseModel):
    message: RequestyMessageSchema


class RequestyChatRequestSchema(BaseModel):
    model: str
    messages: list[RequestyMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class RequestyChatResponseSchema(BaseModel):
    usage: RequestyUsageSchema
    choices: list[RequestyChoiceSchema]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""
        return (self.choices[0].message.content or "").strip()
