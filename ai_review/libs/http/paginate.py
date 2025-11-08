from typing import Awaitable, Callable, TypeVar

from httpx import Response
from pydantic import BaseModel

from ai_review.libs.logger import get_logger

T = TypeVar("T", bound=BaseModel)

logger = get_logger("PAGINATE")


async def paginate(
        fetch_page: Callable[[int | str | None], Awaitable[Response]],
        extract_items: Callable[[Response], list[T]],
        has_next_page: Callable[[Response], bool],
        max_pages: int | None = None,
) -> list[T]:
    """
    Generic page-based pagination helper for APIs using ?page=X pattern.
    """
    page = 1
    items: list[T] = []

    while True:
        response = await fetch_page(page)

        try:
            extracted = extract_items(response)
        except Exception as error:
            logger.error(f"Failed to extract items on {page=}: {error}")
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


async def paginate_with_token(
        fetch_page: Callable[[str | None], Awaitable[Response]],
        extract_items: Callable[[Response], list[T]],
        extract_token: Callable[[Response], str | None],
        max_pages: int | None = None,
) -> list[T]:
    """
    Generic token-based pagination helper for APIs returning continuationToken.
    """
    token: str | None = None
    prev_token: str | None = None
    items: list[T] = []
    page = 1

    while True:
        response = await fetch_page(token)

        try:
            extracted = extract_items(response)
        except Exception as error:
            logger.error(f"Failed to extract items on {page=}: {error}")
            raise RuntimeError(f"Failed to extract items on {page=}") from error

        logger.debug(f"Page {page}: extracted {len(extracted)} items (total={len(items) + len(extracted)})")
        items.extend(extracted)

        token = extract_token(response)
        if not token:
            logger.debug(f"Pagination finished after {page} page(s), total items={len(items)}")
            break

        if token:
            logger.debug(f"Continuation token for next page: {token}")

        page += 1
        if max_pages and page > max_pages:
            logger.error(f"Pagination exceeded {max_pages=}")
            raise RuntimeError(f"Pagination exceeded {max_pages=}")

        if token == prev_token:
            logger.warning(f"Detected repeating continuation token on page {page}, stopping pagination")
            break

        prev_token = token

    return items
