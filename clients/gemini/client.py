from httpx import Response, AsyncHTTPTransport, AsyncClient

from clients.gemini.schema import GeminiChatRequestSchema, GeminiChatResponseSchema
from config import settings
from libs.http.client import HTTPClient
from libs.http.event_hooks.logger import LoggerEventHook
from libs.http.handlers import HTTPClientError, handle_http_error
from libs.http.transports.retry import RetryTransport
from libs.logger import get_logger


class GeminiHTTPClientError(HTTPClientError):
    pass


class GeminiHTTPClient(HTTPClient):
    @handle_http_error(client="GeminiHTTPClient", exception=GeminiHTTPClientError)
    async def chat_api(self, request: GeminiChatRequestSchema) -> Response:
        meta = settings.llm.meta
        return await self.post(
            f"/v1beta/models/{meta.model}:generateContent", json=request.model_dump()
        )

    async def chat(self, request: GeminiChatRequestSchema) -> GeminiChatResponseSchema:
        response = await self.chat_api(request)
        return GeminiChatResponseSchema.model_validate_json(response.text)


def get_gemini_http_client() -> GeminiHTTPClient:
    logger = get_logger("GEMINI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(transport=AsyncHTTPTransport())

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers={"Authorization": f"Bearer {settings.llm.http_client.bearer_token}"},
        base_url=settings.llm.http_client.base_url,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return GeminiHTTPClient(client=client)
