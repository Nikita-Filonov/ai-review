from typing import Protocol

from pydantic import BaseModel


class ChatResultSchema(BaseModel):
    text: str
    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMClientProtocol(Protocol):
    async def chat(self, prompt: str, prompt_system: str) -> ChatResultSchema:
        ...
