from httpx import AsyncClient, AsyncHTTPTransport

from ai_review.clients.azure_devops.pr.client import AzureDevOpsPullRequestsHTTPClient
from ai_review.clients.azure_devops.tools import build_azure_devops_headers
from ai_review.config import settings
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class AzureDevOpsHTTPClient:
    def __init__(self, client: AsyncClient):
        self.pr = AzureDevOpsPullRequestsHTTPClient(client)


def get_azure_devops_http_client() -> AzureDevOpsHTTPClient:
    logger = get_logger("AZURE_DEVOPS_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.vcs.http_client.verify,
        timeout=settings.vcs.http_client.timeout,
        headers=build_azure_devops_headers(),
        base_url=settings.vcs.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response],
        },
    )

    return AzureDevOpsHTTPClient(client=client)
