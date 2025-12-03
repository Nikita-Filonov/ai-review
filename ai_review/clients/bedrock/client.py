from urllib.parse import quote

from httpx import Response, AsyncHTTPTransport, AsyncClient

from ai_review.clients.bedrock.schema import BedrockChatRequestSchema, BedrockChatResponseSchema
from ai_review.clients.bedrock.types import BedrockHTTPClientProtocol
from ai_review.config import settings
from ai_review.libs.aws.signv4 import sign_aws_v4, AwsSigV4Config, AwsCredentials
from ai_review.libs.http.client import HTTPClient
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.handlers import HTTPClientError, handle_http_error
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class BedrockHTTPClientError(HTTPClientError):
    pass


class BedrockHTTPClient(HTTPClient, BedrockHTTPClientProtocol):
    @handle_http_error(client="BedrockHTTPClient", exception=BedrockHTTPClientError)
    async def chat_api(self, request: BedrockChatRequestSchema) -> Response:
        body = request.model_dump_json(exclude_none=True)
        model = quote(settings.llm.meta.model, safe="-._~/")

        route = f"/model/{model}/invoke"
        api_url = settings.llm.http_client.api_url_value.rstrip('/')
        full_url = f"{api_url}{route}"

        return await self.post(
            url=route,
            headers=sign_aws_v4(
                url=full_url,
                body=body,
                method="POST",
                aws_config=AwsSigV4Config(
                    region=settings.llm.http_client.region,
                    service="bedrock"
                ),
                aws_credentials=AwsCredentials(
                    access_key=settings.llm.http_client.access_key,
                    secret_key=settings.llm.http_client.secret_key,
                    session_token=settings.llm.http_client.session_token
                )
            ),
            content=body
        )

    async def chat(self, request: BedrockChatRequestSchema) -> BedrockChatResponseSchema:
        response = await self.chat_api(request)
        return BedrockChatResponseSchema.model_validate_json(response.text)


def get_bedrock_http_client() -> BedrockHTTPClient:
    logger = get_logger("BEDROCK_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)

    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.llm.http_client.verify,
        timeout=settings.llm.http_client.timeout,
        headers={"Content-Type": "application/json"},
        base_url=settings.llm.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return BedrockHTTPClient(client=client)
