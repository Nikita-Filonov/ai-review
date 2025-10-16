from typing import Literal

from pydantic import BaseModel


class ClaudeMessageSchema(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ClaudeChatRequestSchema(BaseModel):
    model: str
    system: str | None = None
    messages: list[ClaudeMessageSchema]
    max_tokens: int | None = None
    temperature: float | None = None


class ClaudeContentSchema(BaseModel):
    type: Literal["text"]
    text: str


class ClaudeUsageSchema(BaseModel):
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class ClaudeChatResponseSchema(BaseModel):
    id: str
    role: str
    usage: ClaudeUsageSchema
    content: list[ClaudeContentSchema]

    @property
    def first_text(self) -> str:
        if not self.content:
            return ""

        return self.content[0].text.strip()
