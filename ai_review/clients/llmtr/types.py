from typing import Protocol

from ai_review.clients.llmtr.schema import (
    LLMTRChatRequestSchema,
    LLMTRChatResponseSchema
)


class LLMTRHTTPClientProtocol(Protocol):
    async def chat(self, request: LLMTRChatRequestSchema) -> LLMTRChatResponseSchema:
        ...
