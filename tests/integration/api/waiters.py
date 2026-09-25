import asyncio
from collections.abc import Awaitable, Callable

from arq.connections import ArqRedis
from arq.constants import abort_jobs_ss, in_progress_key_prefix

WAIT_TIMEOUT = 5.0
WAIT_STEP = 0.01


async def wait_until(
    condition: Callable[[], Awaitable[bool]], message: str
) -> None:
    """Дождаться выполнения условия, иначе — AssertionError с пояснением."""
    try:
        async with asyncio.timeout(WAIT_TIMEOUT):
            while not await condition():
                await asyncio.sleep(WAIT_STEP)
    except TimeoutError:
        raise AssertionError(message) from None


async def wait_for_job_start(arq_redis: ArqRedis, job_id: str) -> None:
    """Дождаться, пока воркер реально начнёт выполнять задачу."""
    key = in_progress_key_prefix + job_id

    async def started() -> bool:
        return bool(await arq_redis.exists(key))

    await wait_until(started, f"Job {job_id} was not started")


async def wait_for_abort_request(arq_redis: ArqRedis, job_id: str) -> None:
    """Дождаться, пока отмена задачи будет отмечена в arq:abort."""

    async def requested() -> bool:
        return await arq_redis.zscore(abort_jobs_ss, job_id) is not None

    await wait_until(requested, f"Abort of job {job_id} was not requested")
