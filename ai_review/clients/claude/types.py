from typing import Protocol

from ai_review.clients.claude.schema import ClaudeChatRequestSchema, ClaudeChatResponseSchema


class ClaudeHTTPClientProtocol(Protocol):
    async def chat(self, request: ClaudeChatRequestSchema) -> ClaudeChatResponseSchema:
        ...
