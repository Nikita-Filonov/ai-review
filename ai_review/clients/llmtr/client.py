from httpx import AsyncClient, Response, AsyncHTTPTransport

from ai_review.clients.llmtr.schema import LLMTRChatRequestSchema, LLMTRChatResponseSchema
from ai_review.clients.llmtr.types import LLMTRHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class LLMTRHTTPClientError(HTTPClientError):
    pass


class LLMTRHTTPClient(HTTPClient, LLMTRHTTPClientProtocol):
    @handle_http_error(client="LLMTRHTTPClient", exception=LLMTRHTTPClientError)
    async def chat_api(self, request: LLMTRChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump(exclude_none=True))

    async def chat(self, request: LLMTRChatRequestSchema) -> LLMTRChatResponseSchema:
        response = await self.chat_api(request)
        return LLMTRChatResponseSchema.model_validate_json(response.text)


def get_llmtr_http_client() -> LLMTRHTTPClient:
    logger = get_logger("LLMTR_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(
            proxy=settings.llm.http_client.proxy_url_value,
            verify=settings.llm.http_client.verify
        )
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers={"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return LLMTRHTTPClient(client=client)
