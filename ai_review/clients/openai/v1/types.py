from typing import Protocol

from ai_review.clients.openai.v1.schema import OpenAIChatRequestSchema, OpenAIChatResponseSchema


class OpenAIV1HTTPClientProtocol(Protocol):
    async def chat(self, request: OpenAIChatRequestSchema) -> OpenAIChatResponseSchema:
        ...
