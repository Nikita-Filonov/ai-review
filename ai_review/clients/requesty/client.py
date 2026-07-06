from httpx import AsyncClient, Response, AsyncHTTPTransport

from ai_review.clients.requesty.schema import RequestyChatRequestSchema, RequestyChatResponseSchema
from ai_review.clients.requesty.types import RequestyHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class RequestyHTTPClientError(HTTPClientError):
    pass


class RequestyHTTPClient(HTTPClient, RequestyHTTPClientProtocol):
    @handle_http_error(client="RequestyHTTPClient", exception=RequestyHTTPClientError)
    async def chat_api(self, request: RequestyChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump(exclude_none=True))

    async def chat(self, request: RequestyChatRequestSchema) -> RequestyChatResponseSchema:
        response = await self.chat_api(request)
        return RequestyChatResponseSchema.model_validate_json(response.text)


def get_requesty_http_client() -> RequestyHTTPClient:
    logger = get_logger("REQUESTY_HTTP_CLIENT")
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

    return RequestyHTTPClient(client=client)
