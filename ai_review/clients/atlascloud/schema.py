from typing import Literal

from pydantic import BaseModel


class AtlasCloudUsageSchema(BaseModel):
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class AtlasCloudMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AtlasCloudChoiceSchema(BaseModel):
    message: AtlasCloudMessageSchema


class AtlasCloudChatRequestSchema(BaseModel):
    model: str
    messages: list[AtlasCloudMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class AtlasCloudChatResponseSchema(BaseModel):
    usage: AtlasCloudUsageSchema
    choices: list[AtlasCloudChoiceSchema]

    @property
    def first_text(self) -> str:
        if not self.choices:
            return ""
        return (self.choices[0].message.content or "").strip()
