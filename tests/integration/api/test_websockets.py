from collections.abc import Callable

import pytest
from arq.connections import ArqRedis
from arq.worker import Function, Worker
from fastapi.testclient import TestClient

from app.api.models.auth import User
from app.core.models.enums import JobStatus
from app.infrastructure.redis.dao.job import ScheduledJobsDAO
from tests.mocks.responses import TaskTestResponse


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    test_client: TestClient,
    user: User,
    arq_redis: ArqRedis,
    scheduled_jobs_dao: ScheduledJobsDAO,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response_ok = TaskTestResponse.test(status=JobStatus.completed)
    response_ok.result = "OK!"
    response = TaskTestResponse.test(
        job_id=response_ok.job.job_id,
        created_at=response_ok.job.created_at,
    )
    await scheduled_jobs_dao.add_job(user.username, response)
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
    user: User,
    arq_redis: ArqRedis,
    scheduled_jobs_dao: ScheduledJobsDAO,
    worker: Callable[..., Worker],
    work_error: Function,
):
    response_error = TaskTestResponse.test(
        status=JobStatus.error, message="Error!"
    )
    response = TaskTestResponse.test(
        job_id=response_error.job.job_id,
        created_at=response_error.job.created_at,
    )
    await scheduled_jobs_dao.add_job(user.username, response)
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
                "file_id": data["job"]["file_id"],
                "prefix": data["job"]["prefix"],
            },
            "task": {},
        }
