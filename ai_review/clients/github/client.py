from httpx import AsyncClient, AsyncHTTPTransport

from ai_review.clients.github.pr.client import GitHubPullRequestsHTTPClient
from ai_review.config import settings
from ai_review.libs.http.event_hooks.logger import LoggerEventHook
from ai_review.libs.http.transports.retry import RetryTransport
from ai_review.libs.logger import get_logger


class GitHubHTTPClient:
    def __init__(self, client: AsyncClient):
        self.pr = GitHubPullRequestsHTTPClient(client)


def get_github_http_client() -> GitHubHTTPClient:
    logger = get_logger("GITHUB_HTTP_CLIENT")
    logger_event_hook = LoggerEventHook(logger=logger)
    retry_transport = RetryTransport(logger=logger, transport=AsyncHTTPTransport())

    client = AsyncClient(
        timeout=settings.llm.http_client.timeout,
        headers={"Authorization": f"Bearer {settings.vcs.http_client.api_token_value}"},
        base_url=settings.vcs.http_client.api_url_value,
        transport=retry_transport,
        event_hooks={
            'request': [logger_event_hook.request],
            'response': [logger_event_hook.response]
        }
    )

    return GitHubHTTPClient(client=client)
