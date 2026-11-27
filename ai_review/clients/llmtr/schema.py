from typing import Literal

from pydantic import BaseModel


class LLMTRUsageSchema(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class LLMTRMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMTRChoiceSchema(BaseModel):
    message: LLMTRMessageSchema


class LLMTRChatRequestSchema(BaseModel):
    model: str
    messages: list[LLMTRMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class LLMTRChatResponseSchema(BaseModel):
    usage: LLMTRUsageSchema
    choices: list[LLMTRChoiceSchema]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""
        return (self.choices[0].message.content or "").strip()
