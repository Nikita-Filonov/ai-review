import pytest
from httpx import Response, Request
from pydantic import BaseModel

from ai_review.libs.http.paginate import paginate, paginate_with_token


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


@pytest.mark.asyncio
async def test_single_page_token_pagination():
    """Should handle a single page with no continuation token."""

    async def fetch_page(_: str | None) -> Response:
        return make_response({"items": [1, 2, 3]})

    def extract_items(response: Response):
        return [DummySchema(value=v) for v in response.json()["items"]]

    def extract_token(_: Response) -> str | None:
        return None  # no more pages

    result = await paginate_with_token(fetch_page, extract_items, extract_token)
    assert [i.value for i in result] == [1, 2, 3]


@pytest.mark.asyncio
async def test_multiple_pages_with_continuation_token():
    """Should iterate over multiple pages using continuation tokens."""
    pages = {
        None: make_response({"items": [1], "continuationToken": "A"}),
        "A": make_response({"items": [2], "continuationToken": "B"}),
        "B": make_response({"items": [3]}),  # last page
    }

    async def fetch_page(token: str | None) -> Response:
        return pages[token]

    def extract_items(response: Response):
        return [DummySchema(value=v) for v in response.json()["items"]]

    def extract_token(response: Response) -> str | None:
        return response.json().get("continuationToken")

    result = await paginate_with_token(fetch_page, extract_items, extract_token)
    assert [i.value for i in result] == [1, 2, 3]


@pytest.mark.asyncio
async def test_extract_items_raises_error():
    """Should raise RuntimeError when extract_items fails."""

    async def fetch_page(_: str | None) -> Response:
        return make_response({"items": [1]})

    def extract_items(_: Response):
        raise ValueError("invalid json")

    def extract_token(_: Response):
        return None

    with pytest.raises(RuntimeError) as exc:
        await paginate_with_token(fetch_page, extract_items, extract_token)
    assert "Failed to extract items" in str(exc.value)


@pytest.mark.asyncio
async def test_max_pages_exceeded_with_token():
    """Should raise error if max_pages limit exceeded."""

    async def fetch_page(_: str | None) -> Response:
        return make_response({"items": [1], "continuationToken": "next"})

    def extract_items(response: Response):
        return [DummySchema(value=v) for v in response.json()["items"]]

    def extract_token(response: Response) -> str | None:
        return response.json().get("continuationToken")

    with pytest.raises(RuntimeError) as exc:
        await paginate_with_token(fetch_page, extract_items, extract_token, max_pages=2)
    assert "Pagination exceeded" in str(exc.value)


@pytest.mark.asyncio
async def test_detects_repeating_token_and_stops():
    """Should stop gracefully if same continuation token repeats."""

    async def fetch_page(token: str | None) -> Response:
        if token is None:
            return make_response({"items": [1], "continuationToken": "X"})
        else:
            # token repeats endlessly
            return make_response({"items": [2], "continuationToken": "X"})

    def extract_items(response: Response):
        return [DummySchema(value=v) for v in response.json()["items"]]

    def extract_token(response: Response) -> str | None:
        return response.json().get("continuationToken")

    items = await paginate_with_token(fetch_page, extract_items, extract_token)
    assert [item.value for item in items] == [1, 2]


@pytest.mark.asyncio
async def test_empty_items_returns_empty_list():
    """Should return empty list if no items at all."""

    async def fetch_page(_: str | None) -> Response:
        return make_response({"items": []})

    def extract_items(_: Response):
        return []

    def extract_token(_: Response) -> str | None:
        return None

    items = await paginate_with_token(fetch_page, extract_items, extract_token)
    assert items == []
