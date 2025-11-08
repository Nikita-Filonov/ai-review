from httpx import AsyncClient, Response, AsyncHTTPTransport

from ai_review.clients.ollama.schema import OllamaChatRequestSchema, OllamaChatResponseSchema
from ai_review.clients.ollama.types import OllamaHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class OllamaHTTPClientError(HTTPClientError):
    pass


class OllamaHTTPClient(HTTPClient, OllamaHTTPClientProtocol):
    @handle_http_error(client="OllamaHTTPClient", exception=OllamaHTTPClientError)
    async def chat_api(self, request: OllamaChatRequestSchema) -> Response:
        return await self.post("/api/chat", json=request.model_dump(exclude_none=True))

    async def chat(self, request: OllamaChatRequestSchema) -> OllamaChatResponseSchema:
        response = await self.chat_api(request)
        return OllamaChatResponseSchema.model_validate_json(response.text)


def get_ollama_http_client() -> OllamaHTTPClient:
    logger = get_logger("OLLAMA_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )
    return OllamaHTTPClient(client=client)
