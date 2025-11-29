from typing import Protocol

from ai_review.clients.bedrock.schema import BedrockChatRequestSchema, BedrockChatResponseSchema


class BedrockHTTPClientProtocol(Protocol):
    async def chat(self, request: BedrockChatRequestSchema) -> BedrockChatResponseSchema:
        ...
