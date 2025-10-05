import pytest
from httpx import Response, Request
from pydantic import BaseModel

from ai_review.libs.http.paginate import paginate


class DummySchema(BaseModel):
    value: int


def make_response(data: dict) -> Response:
    return Response(
        json=data,
        request=Request("GET", "http://test"),
        status_code=200,
    )


@pytest.mark.asyncio
async def test_single_page():
    async def fetch_page(_: int) -> Response:
        return make_response({"items": [1, 2, 3]})

    def extract_items(response: Response) -> list[DummySchema]:
        return [DummySchema(value=value) for value in response.json()["items"]]

    def has_next_page(_: Response) -> bool:
        return False

    items = await paginate(fetch_page, extract_items, has_next_page)
    assert len(items) == 3
    assert [item.value for item in items] == [1, 2, 3]


@pytest.mark.asyncio
async def test_multiple_pages():
    async def fetch_page(page: int) -> Response:
        return make_response({"items": [page]})

    def extract_items(response: Response):
        return [DummySchema(value=value) for value in response.json()["items"]]

    def has_next_page(response: Response) -> bool:
        return response.json()["items"][0] < 3

    items = await paginate(fetch_page, extract_items, has_next_page)
    assert [item.value for item in items] == [1, 2, 3]


@pytest.mark.asyncio
async def test_extract_items_error():
    async def fetch_page(_: int) -> Response:
        return make_response({"items": [1]})

    def extract_items(_: Response):
        raise ValueError("bad json")

    def has_next_page(_: Response) -> bool:
        return False

    with pytest.raises(RuntimeError) as exc:
        await paginate(fetch_page, extract_items, has_next_page)
    assert "Failed to extract items" in str(exc.value)


@pytest.mark.asyncio
async def test_max_pages_exceeded():
    async def fetch_page(page: int) -> Response:
        return make_response({"items": [page]})

    def extract_items(response: Response):
        return [DummySchema(value=value) for value in response.json()["items"]]

    def has_next_page(_: Response) -> bool:
        return True

    with pytest.raises(RuntimeError) as exc:
        await paginate(fetch_page, extract_items, has_next_page, max_pages=2)
    assert "Pagination exceeded" in str(exc.value)


@pytest.mark.asyncio
async def test_empty_items():
    async def fetch_page(_: int) -> Response:
        return make_response({"items": []})

    def extract_items(_: Response):
        return []

    def has_next_page(_: Response) -> bool:
        return False

    result = await paginate(fetch_page, extract_items, has_next_page)
    assert result == []
