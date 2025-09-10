from httpx import Response, AsyncHTTPTransport, AsyncClient

from clients.openai.schema import (
    OpenAIChatCompletionRequestSchema,
    OpenAIChatCompletionResponseSchema
)
from config import settings
from libs.http.client import HTTPClient
from libs.http.event_hooks.logger import LoggerEventHook
from libs.http.handlers import HTTPClientError, handle_http_error
from libs.http.transports.retry import RetryTransport
from libs.logger import get_logger


class OpenAIHTTPClientError(HTTPClientError):
    pass


class OpenAIHTTPClient(HTTPClient):
    @handle_http_error(client='OpenAIHTTPClient', exception=OpenAIHTTPClientError)
    async def chat_completion_api(self, request: OpenAIChatCompletionRequestSchema) -> Response:
        return await self.post("/chat/completions", json=request.model_dump())

    async def chat_completion(
            self,
            request: OpenAIChatCompletionRequestSchema
    ) -> OpenAIChatCompletionResponseSchema:
        response = await self.chat_completion_api(request)
        return OpenAIChatCompletionResponseSchema.model_validate_json(response.text)


def get_openai_http_client() -> OpenAIHTTPClient:
    logger = get_logger("OPENAI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(transport=AsyncHTTPTransport())

    client = AsyncClient(
        headers={"Authorization": f"Bearer {settings.openai.api_token}"},
        base_url=str(settings.openai.api_url),
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return OpenAIHTTPClient(client=client)
