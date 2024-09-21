import asyncio
from collections.abc import Callable

import pytest
from arq.connections import ArqRedis
from arq.jobs import JobStatus as ArqJobStatus
from arq.worker import Function, Worker
from fastapi.testclient import TestClient

from app.core.models.enums import JobStatus
from tests.mocks.responses import TaskTestResponse


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    test_client: TestClient,
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response_ok = TaskTestResponse.test(
        status=JobStatus.completed, message="Job is completed"
    )
    response = TaskTestResponse.test(job_id=response_ok.job.job_id)
    job = await arq_redis.enqueue_job(
        work_ok.name, response, _job_id=response.job.job_id
    )
    worker_ = worker(functions=[work_ok])
    await worker_.main()
    assert await job.result() == "OK!"
    with test_client.websocket_connect(
        f"/jobs/{response.job.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == response_ok.model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_error(
    test_client: TestClient,
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
    with test_client.websocket_connect(
        f"/jobs/{response.job.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == response_error.model_dump(
            mode="json", exclude_none=True
        )


@pytest.mark.asyncio(scope="session")
async def test_job_abort(
    test_client: TestClient,
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    work_long: Function,
):
    response = TaskTestResponse.test()
    job = await arq_redis.enqueue_job(
        work_long.name, response, _job_id=response.job.job_id
    )
    async with asyncio.timeout(10):
        while ArqJobStatus.queued is not await job.status():
            await asyncio.sleep(0.1)
    worker_ = worker(functions=[work_long], allow_abort_jobs=True)
    asyncio.create_task(worker_.main())
    with test_client.websocket_connect(
        f"/jobs/{response.job.job_id}/ws?abort_on_disconnect=true"
    ):
        await asyncio.sleep(0.1)
    with pytest.raises(asyncio.CancelledError):
        await job.result()


def test_job_is_not_found(test_client: TestClient):
    job_id = "unknown_job_id"
    with test_client.websocket_connect(f"/jobs/{job_id}/ws") as websocket:
        data = websocket.receive_json()
        assert data == {
            "job": {
                "job_id": job_id,
                "message": "Job is not found",
                "status": JobStatus.not_found.value,
                "created_at": data["job"]["created_at"],
            },
            "task": {},
        }
