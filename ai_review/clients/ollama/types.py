from typing import Protocol

from ai_review.clients.ollama.schema import OllamaChatRequestSchema, OllamaChatResponseSchema


class OllamaHTTPClientProtocol(Protocol):
    async def chat(self, request: OllamaChatRequestSchema) -> OllamaChatResponseSchema:
        ...
