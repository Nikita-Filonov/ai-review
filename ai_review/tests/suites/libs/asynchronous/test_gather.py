import asyncio

import pytest

from ai_review.config import settings
from ai_review.libs.asynchronous.gather import bounded_gather


@pytest.mark.asyncio
async def test_bounded_gather_limits_concurrency(monkeypatch: pytest.MonkeyPatch):
    concurrency_limit = 3
    monkeypatch.setattr(settings.core, "concurrency", concurrency_limit)

    active = 0
    max_active = 0

    async def task(number: int):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.05)
        active -= 1
        return number * 2

    results = await bounded_gather(task(index) for index in range(10))

    assert max_active <= concurrency_limit
    assert results == tuple(index * 2 for index in range(10))


@pytest.mark.asyncio
async def test_bounded_gather_returns_exceptions(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings.core, "concurrency", 2)

    async def ok_task():
        await asyncio.sleep(0.01)
        return "ok"

    async def fail_task():
        raise ValueError("boom")

    results = await bounded_gather([ok_task(), fail_task(), ok_task()])

    assert len(results) == 3
    assert any(isinstance(result, Exception) for result in results)
    assert any(r == "ok" for r in results)
