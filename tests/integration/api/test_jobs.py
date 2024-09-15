from collections.abc import Callable

import pytest
from arq.connections import ArqRedis
from arq.worker import Function, Worker
from httpx import AsyncClient

from app.core.models.enums import JobStatus
from tests.mocks.responses import TaskTestResponse


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    client: AsyncClient,
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response_ok = TaskTestResponse.test(status=JobStatus.completed)
    response = TaskTestResponse.test(job_id=response_ok.job.job_id)
    job = await arq_redis.enqueue_job(
        work_ok.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[work_ok])
    await worker_.main()
    assert await job.result() == "OK!"
    resp = await client.get(f"/jobs/{response.job.job_id}")
    assert resp.is_success
    data = resp.json()
    assert data == response_ok.model_dump(exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_error(
    client: AsyncClient,
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    work_error: Function,
):
    response_error = TaskTestResponse.test(
        status=JobStatus.error, message="Error!"
    )
    response = TaskTestResponse.test(job_id=response_error.job.job_id)
    job = await arq_redis.enqueue_job(
        work_error.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[work_error])
    await worker_.main()
    with pytest.raises(ValueError):
        await job.result()
    resp = await client.get(f"/jobs/{response.job.job_id}")
    assert resp.is_success
    data = resp.json()
    assert data == response_error.model_dump(exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_is_not_found(client: AsyncClient):
    job_id = "unknown_job_id"
    resp = await client.get(f"/jobs/{job_id}")
    assert resp.is_success
    data = resp.json()
    assert data == {
        "job": {
            "job_id": job_id,
            "status": JobStatus.not_found.value,
        },
        "task": {},
    }
