from httpx import Response, AsyncHTTPTransport, AsyncClient

from ai_review.clients.openai.v1.schema import OpenAIChatRequestSchema, OpenAIChatResponseSchema
from ai_review.clients.openai.v1.types import OpenAIV1HTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class OpenAIV1HTTPClientError(HTTPClientError):
    pass


class OpenAIV1HTTPClient(HTTPClient, OpenAIV1HTTPClientProtocol):
    @handle_http_error(client='OpenAIV1HTTPClient', exception=OpenAIV1HTTPClientError)
    async def chat_api(self, request: OpenAIChatRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump(exclude_none=True))

    async def chat(self, request: OpenAIChatRequestSchema) -> OpenAIChatResponseSchema:
        response = await self.chat_api(request)
        return OpenAIChatResponseSchema.model_validate_json(response.text)


def get_openai_v1_http_client() -> OpenAIV1HTTPClient:
    logger = get_logger("OPENAI_V1_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers={"Authorization": f"Bearer {settings.llm.http_client.api_token_value}"},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return OpenAIV1HTTPClient(client=client)
