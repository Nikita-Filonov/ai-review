from httpx import AsyncClient, Response, AsyncHTTPTransport

from ai_review.clients.atlascloud.schema import AtlasCloudChatRequestSchema, AtlasCloudChatResponseSchema
from ai_review.clients.atlascloud.types import AtlasCloudHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class AtlasCloudHTTPClientError(HTTPClientError):
    pass


class AtlasCloudHTTPClient(HTTPClient, AtlasCloudHTTPClientProtocol):
    @handle_http_error(client="AtlasCloudHTTPClient", exception=AtlasCloudHTTPClientError)
    async def chat_api(self, request: AtlasCloudChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump(exclude_none=True))

    async def chat(self, request: AtlasCloudChatRequestSchema) -> AtlasCloudChatResponseSchema:
        response = await self.chat_api(request)
        return AtlasCloudChatResponseSchema.model_validate_json(response.text)


def get_atlascloud_http_client() -> AtlasCloudHTTPClient:
    logger = get_logger("ATLASCLOUD_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(
            proxy=settings.llm.http_client.proxy_url_value,
            verify=settings.llm.http_client.verify
        )
    )

    headers = {"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"}
    if settings.llm.meta.title:
        headers["X-Title"] = settings.llm.meta.title

    if settings.llm.meta.referer:
        headers["Referer"] = settings.llm.meta.referer

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers=headers,
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return AtlasCloudHTTPClient(client=client)
