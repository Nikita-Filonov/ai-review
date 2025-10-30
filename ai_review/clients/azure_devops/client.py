import base64
from httpx import AsyncClient, AsyncHTTPTransport

from ai_review.clients.azure_devops.pr.client import AzureDevOpsPullRequestsHTTPClient
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
    retry_transport = RetryTransport(logger=logger, transport=AsyncHTTPTransport())

    # Azure DevOps uses Basic authentication with PAT
    # Format: Basic <base64(":PAT")>
    pat_token = settings.vcs.http_client.api_token_value
    # Encode ":PAT" (empty username, colon, PAT token) to base64
    credentials = base64.b64encode(f":{pat_token}".encode()).decode()
    
    client = AsyncClient(
        timeout=settings.vcs.http_client.timeout,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json"
        },
        base_url=settings.vcs.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return AzureDevOpsHTTPClient(client=client)

