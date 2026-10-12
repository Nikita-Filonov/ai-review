from typing import Protocol

from pydantic import BaseModel, Field


class ChatResultSchema(BaseModel):
    text: str
    # Responses API models can return several assistant message blocks in a
    # single response. Keep those boundaries for agent-mode parsing while
    # retaining ``text`` for existing callers.
    texts: list[str] = Field(default_factory=list)
    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMClientProtocol(Protocol):
    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        ...
