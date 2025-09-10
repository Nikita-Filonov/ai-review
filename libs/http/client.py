from typing import Any

from httpx import AsyncClient, Response, QueryParams


class HTTPClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def get(self, url: str, query: QueryParams | None = None) -> Response:
        return await self.client.get(url=url, params=query)

    async def post(self, url: str, json: Any | None = None) -> Response:
        return await self.client.post(url=url, json=json)
