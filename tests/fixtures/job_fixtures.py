import asyncio
from typing import Any, Callable

import pytest_asyncio
from arq.connections import ArqRedis
from arq.jobs import Job
from arq.worker import Worker, func

from app.core.models.schemas import TaskResponse


@pytest_asyncio.fixture(scope="session")
async def job_ok(
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    test_response_ok: TaskResponse,
) -> Job:
    async def perform_work_ok(
        ctx: dict[str, Any], response: TaskResponse
    ) -> None:
        print("OK!")

    job = await arq_redis.enqueue_job(
        "perform_work_ok",
        test_response_ok,
        _job_id=test_response_ok.job.job_id,
    )
    worker_ = worker(functions=[func(perform_work_ok, name="perform_work_ok")])
    await worker_.main()
    return job


@pytest_asyncio.fixture(scope="session")
async def job_error(
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    test_response_error: TaskResponse,
) -> Job:
    async def perform_work_error(
        ctx: dict[str, Any], response: TaskResponse
    ) -> None:
        raise ValueError("Error!")

    job = await arq_redis.enqueue_job(
        "perform_work_error",
        test_response_error,
        _job_id=test_response_error.job.job_id,
    )
    worker_ = worker(
        functions=[func(perform_work_error, name="perform_work_error")]
    )
    await worker_.main()
    return job


@pytest_asyncio.fixture(scope="session")
async def job_abort(
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    test_response: TaskResponse,
) -> Job:
    async def perform_work_abort(
        ctx: dict[str, Any], response: TaskResponse
    ) -> None:
        await asyncio.sleep(3600)

    job = await arq_redis.enqueue_job(
        "perform_work_abort", test_response, _job_id=test_response.job.job_id
    )
    worker_ = worker(
        functions=[func(perform_work_abort, name="perform_work_abort")],
        allow_abort_jobs=True,
    )
    asyncio.get_running_loop().create_task(worker_.main())
    return job
