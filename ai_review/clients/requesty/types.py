from typing import Protocol

from ai_review.clients.requesty.schema import (
    RequestyChatRequestSchema,
    RequestyChatResponseSchema
)


class RequestyHTTPClientProtocol(Protocol):
    async def chat(self, request: RequestyChatRequestSchema) -> RequestyChatResponseSchema:
        ...
