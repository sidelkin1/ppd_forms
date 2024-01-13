import asyncio
from typing import Callable

import pytest
from arq.connections import ArqRedis
from arq.worker import Worker, func
from fastapi.testclient import TestClient

from app.core.models.enums import JobStatus
from tests.fixtures.response_constants import TaskTestResponse
from tests.fixtures.worker_constants import work_error, work_long, work_ok


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    test_client: TestClient, arq_redis: ArqRedis, worker: Callable[..., Worker]
):
    function = func(work_ok, name="work_ok")
    response_ok = TaskTestResponse.test(
        status=JobStatus.completed, message="Job is completed"
    )
    response = TaskTestResponse.test(job_id=response_ok.job.job_id)
    job = await arq_redis.enqueue_job(
        function.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[function])
    await worker_.main()
    assert await job.result() == "OK!"
    with test_client.websocket_connect(
        f"jobs/{response.job.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == response_ok.model_dump(exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_error(
    test_client: TestClient, arq_redis: ArqRedis, worker: Callable[..., Worker]
):
    function = func(work_error, name="work_error")
    response_error = TaskTestResponse.test(
        status=JobStatus.error, message="Error!"
    )
    response = TaskTestResponse.test(job_id=response_error.job.job_id)
    job = await arq_redis.enqueue_job(
        function.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[function])
    await worker_.main()
    with pytest.raises(ValueError):
        await job.result()
    with test_client.websocket_connect(
        f"jobs/{response.job.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == response_error.model_dump(exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_abort(
    test_client: TestClient, arq_redis: ArqRedis, worker: Callable[..., Worker]
):
    function = func(work_long, name="work_long")
    response = TaskTestResponse.test()
    job = await arq_redis.enqueue_job(
        function.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[function], allow_abort_jobs=True)
    asyncio.create_task(worker_.main())
    with test_client.websocket_connect(f"jobs/{response.job.job_id}/ws"):
        await asyncio.sleep(0.1)
    with pytest.raises(asyncio.CancelledError):
        await job.result()


def test_job_is_not_found(test_client: TestClient):
    job_id = "unknown_job_id"
    with test_client.websocket_connect(f"jobs/{job_id}/ws") as websocket:
        data = websocket.receive_json()
        assert data == {
            "job": {
                "job_id": job_id,
                "message": "Job is not found",
                "status": JobStatus.not_found.value,
            }
        }
