from httpx import AsyncClient, Response, AsyncHTTPTransport

from clients.claude.schema import ClaudeChatRequestSchema, ClaudeChatResponseSchema
from config import settings
from libs.http.client import HTTPClient
from libs.http.event_hooks.logger import LoggerEventHook
from libs.http.handlers import HTTPClientError, handle_http_error
from libs.http.transports.retry import RetryTransport
from libs.logger import get_logger


class ClaudeHTTPClientError(HTTPClientError):
    pass


class ClaudeHTTPClient(HTTPClient):
    @handle_http_error(client="ClaudeHTTPClient", exception=ClaudeHTTPClientError)
    async def chat_api(self, request: ClaudeChatRequestSchema) -> Response:
        return await self.post("/v1/messages", json=request.model_dump())

    async def chat(self, request: ClaudeChatRequestSchema) -> ClaudeChatResponseSchema:
        response = await self.chat_api(request)
        return ClaudeChatResponseSchema.model_validate_json(response.text)


def get_claude_http_client() -> ClaudeHTTPClient:
    logger = get_logger("CLAUDE_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(transport=AsyncHTTPTransport())

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers={
            "x-api-key": settings.llm.http_client.bearer_token,
            "anthropic-version": settings.llm.http_client.api_version,
        },
        base_url=settings.llm.http_client.base_url,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )
    return ClaudeHTTPClient(client=client)
