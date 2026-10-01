import asyncio

import pytest

from app.core.utils.concurrency_limit import concurrency_limit

LIMIT = 3
WORKERS = 5


@pytest.mark.asyncio
async def test_concurrency_limit_caps_parallel_tasks():
    """Одновременно в критической секции не больше limit задач."""
    active = 0
    peak = 0
    entered = asyncio.Semaphore(0)
    release = asyncio.Event()

    async def worker() -> None:
        nonlocal active, peak
        async with concurrency_limit("fnv", LIMIT):
            active += 1
            peak = max(peak, active)
            entered.release()
            await release.wait()
            active -= 1

    tasks = [asyncio.create_task(worker()) for _ in range(WORKERS)]
    for _ in range(LIMIT):
        await entered.acquire()
    for _ in range(10):
        await asyncio.sleep(0)

    assert active == LIMIT
    assert all(not task.done() for task in tasks)

    release.set()
    await asyncio.gather(*tasks)

    assert active == 0
    assert peak == LIMIT


@pytest.mark.asyncio
async def test_concurrency_limit_is_shared_per_name():
    """Разные имена - независимые семафоры."""
    release = asyncio.Event()
    entered = asyncio.Semaphore(0)

    async def hold() -> None:
        async with concurrency_limit("busy", 1):
            entered.release()
            await release.wait()

    task = asyncio.create_task(hold())
    await entered.acquire()
    # "busy" занят этой задачей, но "free" от него не зависит
    async with concurrency_limit("free", 1):
        pass
    release.set()
    await task


async def _acquire_once() -> bool:
    async with concurrency_limit("per-loop", 1):
        return True


def test_concurrency_limit_is_per_loop():
    """Занятый лимит одного цикла не блокирует другой цикл."""
    first = asyncio.new_event_loop()
    second = asyncio.new_event_loop()

    async def saturate() -> tuple[asyncio.Task, asyncio.Event]:
        release = asyncio.Event()

        async def hold() -> None:
            async with concurrency_limit("per-loop", 1):
                await release.wait()

        task = asyncio.create_task(hold())
        await asyncio.sleep(0)
        return task, release

    try:
        task, release = first.run_until_complete(saturate())
        # цикл second не должен ждать семафор, занятый в first
        assert second.run_until_complete(
            asyncio.wait_for(_acquire_once(), timeout=5)
        )
        release.set()
        first.run_until_complete(task)
    finally:
        first.close()
        second.close()
