from typing import Protocol

from ai_review.clients.atlascloud.schema import (
    AtlasCloudChatRequestSchema,
    AtlasCloudChatResponseSchema
)


class AtlasCloudHTTPClientProtocol(Protocol):
    async def chat(self, request: AtlasCloudChatRequestSchema) -> AtlasCloudChatResponseSchema:
        ...
