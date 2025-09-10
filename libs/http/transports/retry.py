import asyncio
from http import HTTPStatus

from httpx import Request, Response, AsyncBaseTransport


class RetryTransport(AsyncBaseTransport):
    def __init__(
            self,
            transport: AsyncBaseTransport,
            max_retries: int = 5,
            retry_delay: float = 0.5,
            retry_status_codes: tuple[HTTPStatus, ...] = (
                    HTTPStatus.BAD_GATEWAY,
                    HTTPStatus.GATEWAY_TIMEOUT,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    ):
        self.transport = transport
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_status_codes = retry_status_codes

    async def handle_async_request(self, request: Request) -> Response:
        response: Response | None = None
        for _ in range(self.max_retries):
            response = await self.transport.handle_async_request(request)
            if response.status_code not in self.retry_status_codes:
                return response

            await asyncio.sleep(self.retry_delay)

        return response
