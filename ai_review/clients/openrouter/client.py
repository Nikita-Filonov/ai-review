from httpx import AsyncClient, Response, AsyncHTTPTransport

from ai_review.clients.openrouter.schema import OpenRouterChatRequestSchema, OpenRouterChatResponseSchema
from ai_review.clients.openrouter.types import OpenRouterHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class OpenRouterHTTPClientError(HTTPClientError):
    pass


class OpenRouterHTTPClient(HTTPClient, OpenRouterHTTPClientProtocol):
    @handle_http_error(client="OpenRouterHTTPClient", exception=OpenRouterHTTPClientError)
    async def chat_api(self, request: OpenRouterChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump(exclude_none=True))

    async def chat(self, request: OpenRouterChatRequestSchema) -> OpenRouterChatResponseSchema:
        response = await self.chat_api(request)
        return OpenRouterChatResponseSchema.model_validate_json(response.text)


def get_openrouter_http_client() -> OpenRouterHTTPClient:
    logger = get_logger("OPENROUTER_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(logger=logger, transport=AsyncHTTPTransport())

    headers = {"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"}
    if settings.llm.meta.title:
        headers["X-Title"] = settings.llm.meta.title

    if settings.llm.meta.referer:
        headers["Referer"] = settings.llm.meta.referer

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers=headers,
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return OpenRouterHTTPClient(client=client)
