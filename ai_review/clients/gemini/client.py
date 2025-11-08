from httpx import Response, AsyncHTTPTransport, AsyncClient

from ai_review.clients.gemini.schema import GeminiChatRequestSchema, GeminiChatResponseSchema
from ai_review.clients.gemini.types import GeminiHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class GeminiHTTPClientError(HTTPClientError):
    pass


class GeminiHTTPClient(HTTPClient, GeminiHTTPClientProtocol):
    @handle_http_error(client="GeminiHTTPClient", exception=GeminiHTTPClientError)
    async def chat_api(self, request: GeminiChatRequestSchema) -> Response:
        meta = settings.llm.meta
        return await self.post(
            f"/v1beta/models/{meta.model}:generateContent",
            json=request.model_dump(exclude_none=True)
        )

    async def chat(self, request: GeminiChatRequestSchema) -> GeminiChatResponseSchema:
        response = await self.chat_api(request)
        return GeminiChatResponseSchema.model_validate_json(response.text)


def get_gemini_http_client() -> GeminiHTTPClient:
    logger = get_logger("GEMINI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers={"x-goog-api-key": settings.llm.http_client.api_token_value},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return GeminiHTTPClient(client=client)
