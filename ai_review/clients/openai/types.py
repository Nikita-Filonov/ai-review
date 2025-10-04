from typing import Protocol

from ai_review.clients.openai.schema import OpenAIChatRequestSchema, OpenAIChatResponseSchema


class OpenAIHTTPClientProtocol(Protocol):
    async def chat(self, request: OpenAIChatRequestSchema) -> OpenAIChatResponseSchema:
        ...
