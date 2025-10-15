from typing import Protocol

from ai_review.clients.openrouter.schema import (
    OpenRouterChatRequestSchema,
    OpenRouterChatResponseSchema
)


class OpenRouterHTTPClientProtocol(Protocol):
    async def chat(self, request: OpenRouterChatRequestSchema) -> OpenRouterChatResponseSchema:
        ...
