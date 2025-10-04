from typing import Protocol

from ai_review.clients.gemini.schema import GeminiChatRequestSchema, GeminiChatResponseSchema


class GeminiHTTPClientProtocol(Protocol):
    async def chat(self, request: GeminiChatRequestSchema) -> GeminiChatResponseSchema:
        ...
