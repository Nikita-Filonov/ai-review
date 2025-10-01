import asyncio
from typing import Awaitable, Iterable, TypeVar

from ai_review.config import settings

T = TypeVar("T")


async def bounded_gather(coroutines: Iterable[Awaitable[T]]) -> tuple[T, ...]:
    sem = asyncio.Semaphore(settings.core.concurrency)

    async def wrap(coro: Awaitable[T]) -> T:
        async with sem:
            return await coro

    results = await asyncio.gather(*(wrap(coroutine) for coroutine in coroutines), return_exceptions=True)
    return tuple(results)
