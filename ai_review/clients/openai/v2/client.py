from httpx import Response, AsyncClient, AsyncHTTPTransport

from ai_review.clients.openai.v2.schema import (
    OpenAIResponsesRequestSchema,
    OpenAIResponsesResponseSchema
)
from ai_review.clients.openai.v2.types import OpenAIV2HTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class OpenAIV2HTTPClientError(HTTPClientError):
    pass


class OpenAIV2HTTPClient(HTTPClient, OpenAIV2HTTPClientProtocol):
    @handle_http_error(client='OpenAIV2HTTPClient', exception=OpenAIV2HTTPClientError)
    async def chat_api(self, request: OpenAIResponsesRequestSchema) -> Response:
        return await self.post("/responses", json=request.model_dump(exclude_none=True))

    async def chat(self, request: OpenAIResponsesRequestSchema) -> OpenAIResponsesResponseSchema:
        response = await self.chat_api(request)
        return OpenAIResponsesResponseSchema.model_validate_json(response.text)


def get_openai_v2_http_client() -> OpenAIV2HTTPClient:
    logger = get_logger("OPENAI_V2_HTTP_CLIENT")
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

    return OpenAIV2HTTPClient(client=client)
