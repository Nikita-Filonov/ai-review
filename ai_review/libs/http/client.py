from typing import Any

from httpx import AsyncClient, Response, QueryParams
from httpx._types import HeaderTypes, RequestContent


class HTTPClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def get(self, url: str, query: QueryParams | None = None) -> Response:
        return await self.client.get(url=url, params=query, follow_redirects=True)

    async def post(
            self,
            url: str,
            json: Any | None = None,
            query: QueryParams | None = None,
            headers: HeaderTypes | None = None,
            content: RequestContent | None = None,
    ) -> Response:
        return await self.client.post(url=url, json=json, params=query, headers=headers, content=content)
