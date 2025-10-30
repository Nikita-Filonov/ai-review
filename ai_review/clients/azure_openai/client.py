from httpx import Response, AsyncHTTPTransport, AsyncClient

from ai_review.clients.azure_openai.schema import (
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
    async def chat_api(self, request: AzureOpenAIChatRequestSchema, api_version: str, deployment_name: str) -> Response:
        url = f"/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
        return await self.post(
            url,
            json=request.model_dump(exclude_none=True)
        )

    async def chat(self, request: AzureOpenAIChatRequestSchema) -> AzureOpenAIChatResponseSchema:
        response = await self.chat_api(
            request,
            api_version=settings.llm.meta.api_version,
            deployment_name=settings.llm.meta.deployment_name
        )
        return AzureOpenAIChatResponseSchema.model_validate_json(response.text)


def get_azure_openai_http_client() -> AzureOpenAIHTTPClient:
    logger = get_logger("AZURE_OPENAI_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(logger=logger, transport=AsyncHTTPTransport())

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers={
            "api-key": settings.llm.http_client.api_token_value,
            "Content-Type": "application/json"
        },
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return AzureOpenAIHTTPClient(client=client)

