import asyncio
from typing import Awaitable, Iterable, TypeVar

T = TypeVar("T")


async def bounded_gather(coroutines: Iterable[Awaitable[T]], concurrency: int = 32) -> tuple[T, ...]:
    sem = asyncio.Semaphore(concurrency)

    async def wrap(coro: Awaitable[T]) -> T:
        async with sem:
            return await coro

    return await asyncio.gather(*(wrap(coroutine) for coroutine in coroutines), return_exceptions=True)
