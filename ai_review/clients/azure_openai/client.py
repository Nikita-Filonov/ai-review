from httpx import Response, AsyncHTTPTransport, AsyncClient, QueryParams

from ai_review.clients.azure_openai.schema import (
    AzureOpenAIChatQuerySchema,
    AzureOpenAIChatRequestSchema,
    AzureOpenAIChatResponseSchema
)
from ai_review.clients.azure_openai.types import AzureOpenAIHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class AzureOpenAIHTTPClientError(HTTPClientError):
    pass


class AzureOpenAIHTTPClient(HTTPClient, AzureOpenAIHTTPClientProtocol):
    @handle_http_error(client='AzureOpenAIHTTPClient', exception=AzureOpenAIHTTPClientError)
    async def chat_api(self, request: AzureOpenAIChatRequestSchema) -> Response:
        query = AzureOpenAIChatQuerySchema(api_version=settings.llm.http_client.api_version)
        return await self.post(
            f"/openai/deployments/{settings.llm.meta.model}/chat/completions",
            json=request.model_dump(exclude_none=True),
            query=QueryParams(**query.model_dump(by_alias=True)),

        )

    async def chat(self, request: AzureOpenAIChatRequestSchema) -> AzureOpenAIChatResponseSchema:
        response = await self.chat_api(request)
        return AzureOpenAIChatResponseSchema.model_validate_json(response.text)


def get_azure_openai_http_client() -> AzureOpenAIHTTPClient:
    logger = get_logger("AZURE_OPENAI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)

    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify),
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers={"api-key": settings.llm.http_client.api_token_value},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return AzureOpenAIHTTPClient(client=client)
