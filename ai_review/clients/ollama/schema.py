from typing import Literal

from pydantic import BaseModel, Field


class OllamaMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class OllamaOptionsSchema(BaseModel):
    stop: list[str] | None = None
    seed: int | None = None
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    num_predict: int | None = Field(default=None, ge=1)
    repeat_penalty: float | None = Field(default=None, ge=0.0)


class OllamaChatRequestSchema(BaseModel):
    model: str
    stream: bool = False
    options: OllamaOptionsSchema | None = None
    messages: list[OllamaMessageSchema]


class OllamaUsageSchema(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None

    @property
    def total_tokens(self) -> int | None:
        if (self.prompt_tokens is not None) and (self.completion_tokens is not None):
            return self.prompt_tokens + self.completion_tokens

        return None


class OllamaChatResponseSchema(BaseModel):
    done: bool = Field(default=True)
    usage: OllamaUsageSchema | None = None
    model: str
    message: OllamaMessageSchema

    @property
    def first_text(self) -> str:
        return (self.message.content or "").strip()
