import httpx2
import pytest

from ai_review.libs.http.transports.retry import NO_RETRY, RetryTransport
from ai_review.libs.logger import get_logger


class CountingTransport(httpx2.AsyncBaseTransport):
    """Inner transport that always answers with the same status and counts attempts."""

    def __init__(self, status_code: int):
        self.status_code = status_code
        self.attempts = 0

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        self.attempts += 1
        return httpx2.Response(self.status_code, request=request)


def build_retry_transport(inner: CountingTransport) -> RetryTransport:
    return RetryTransport(
        logger=get_logger("TEST_RETRY_TRANSPORT"),
        transport=inner,
        max_retries=3,
        retry_delay=0,
    )


@pytest.mark.asyncio
async def test_retry_transport_retries_server_errors():
    """Should exhaust max_retries when the server keeps answering 500."""
    inner = CountingTransport(status_code=500)
    transport = build_retry_transport(inner)

    response = await transport.handle_async_request(httpx2.Request("POST", "https://gitlab.test/api"))

    assert response.status_code == 500
    assert inner.attempts == 3


@pytest.mark.asyncio
async def test_retry_transport_does_not_retry_when_opted_out():
    """Should make a single attempt for a request marked as non-idempotent."""
    inner = CountingTransport(status_code=500)
    transport = build_retry_transport(inner)
    request = httpx2.Request("POST", "https://gitlab.test/api", extensions=NO_RETRY)

    response = await transport.handle_async_request(request)

    assert response.status_code == 500
    assert inner.attempts == 1


@pytest.mark.asyncio
async def test_retry_transport_returns_success_without_retrying():
    """Should return a successful response on the first attempt."""
    inner = CountingTransport(status_code=200)
    transport = build_retry_transport(inner)

    response = await transport.handle_async_request(httpx2.Request("GET", "https://gitlab.test/api"))

    assert response.status_code == 200
    assert inner.attempts == 1
