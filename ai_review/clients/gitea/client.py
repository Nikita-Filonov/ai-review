from httpx import AsyncClient, AsyncHTTPTransport

from ai_review.clients.gitea.pr.client import GiteaPullRequestsHTTPClient
from ai_review.config import settings
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class GiteaHTTPClient:
    def __init__(self, client: AsyncClient):
        self.pr = GiteaPullRequestsHTTPClient(client)


def get_gitea_http_client() -> GiteaHTTPClient:
    logger = get_logger("GITEA_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(
        logger=logger,
        transport=AsyncHTTPTransport(verify=settings.vcs.http_client.verify)
    )

    client = AsyncClient(
        verify=settings.vcs.http_client.verify,
        timeout=settings.vcs.http_client.timeout,
        headers={"Authorization": f"token {settings.vcs.http_client.api_token_value}"},
        base_url=settings.vcs.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            "request": [logger_event_hook.request],
            "response": [logger_event_hook.response]
        }
    )

    return GiteaHTTPClient(client=client)
