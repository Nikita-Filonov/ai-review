import asyncio
from typing import Awaitable, Iterable, TypeVar

from ai_review.config import settings
from ai_review.libs.logger import get_logger

logger = get_logger("GATHER")

T = TypeVar("T")


async def bounded_gather(coroutines: Iterable[Awaitable[T]]) -> tuple[T, ...]:
    sem = asyncio.Semaphore(settings.core.concurrency)

    async def wrap(coro: Awaitable[T]) -> T:
        async with sem:
            try:
                return await coro
            except Exception as error:
                logger.warning(f"Task failed: {type(error).__name__}: {error}")
                return error

    results = await asyncio.gather(*(wrap(coroutine) for coroutine in coroutines), return_exceptions=True)
    return tuple(results)
