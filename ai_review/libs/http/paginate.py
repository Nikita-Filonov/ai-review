from typing import Awaitable, Callable, TypeVar

from httpx import Response
from pydantic import BaseModel

from ai_review.libs.logger import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger("PAGINATE")


async def paginate(
        fetch_page: Callable[[int], Awaitable[Response]],
        extract_items: Callable[[Response], list[T]],
        has_next_page: Callable[[Response], bool],
        max_pages: int | None = None,
) -> list[T]:
    page = 1
    items: list[T] = []

    while True:
        response = await fetch_page(page)

        try:
            extracted = extract_items(response)
        except Exception as error:
            logger.error(f"Failed to extract items on {page=}")
            raise RuntimeError(f"Failed to extract items on {page=}") from error

        logger.debug(f"Page {page}: extracted {len(extracted)} items (total={len(items) + len(extracted)})")
        items.extend(extracted)

        if not has_next_page(response):
            logger.debug(f"Pagination finished after {page} page(s), total items={len(items)}")
            break

        page += 1
        if max_pages and (page > max_pages):
            logger.error(f"Pagination exceeded {max_pages=}")
            raise RuntimeError(f"Pagination exceeded {max_pages=}")

    return items
