from httpx import Response, AsyncHTTPTransport, AsyncClient

from ai_review.clients.openai.schema import OpenAIChatRequestSchema, OpenAIChatResponseSchema
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class OpenAIHTTPClientError(HTTPClientError):
    pass


class OpenAIHTTPClient(HTTPClient):
    @handle_http_error(client='OpenAIHTTPClient', exception=OpenAIHTTPClientError)
    async def chat_api(self, request: OpenAIChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump())

    async def chat(self, request: OpenAIChatRequestSchema) -> OpenAIChatResponseSchema:
        response = await self.chat_api(request)
        return OpenAIChatResponseSchema.model_validate_json(response.text)


def get_openai_http_client() -> OpenAIHTTPClient:
    logger = get_logger("OPENAI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(logger=logger, transport=AsyncHTTPTransport())

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers={"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return OpenAIHTTPClient(client=client)
