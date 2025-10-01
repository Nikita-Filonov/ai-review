from typing import TYPE_CHECKING

from httpx import Request, Response

from ai_review.libs.http.event_hooks.base import BaseEventHook

if TYPE_CHECKING:
    from loguru import Logger


class LoggerEventHook(BaseEventHook):
    def __init__(self, logger: "Logger"):
        self.logger = logger

    async def request(self, request: Request):
        self.logger.info(f"{request.method} {request.url} - Waiting for response")

    async def response(self, response: Response):
        request = response.request
        self.logger.info(f"{request.method} {request.url} - Status {response.status_code}")
