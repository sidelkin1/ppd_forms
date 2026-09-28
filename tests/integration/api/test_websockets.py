import asyncio
from collections.abc import Callable

import pytest
from arq.connections import ArqRedis
from arq.worker import Function, Worker
from fastapi.testclient import TestClient

from app.api.models.auth import User
from app.core.models.enums import JobStatus
from app.infrastructure.redis.dao.arq import ArqDAO
from tests.integration.api.waiters import (
    wait_for_abort_request,
    wait_for_job_start,
)
from tests.mocks.responses import TaskTestResponse


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    test_client: TestClient,
    user: User,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response_ok = TaskTestResponse.test(status=JobStatus.completed)
    response_ok.result = "OK!"
    response = TaskTestResponse.test(
        job_id=response_ok.job.job_id,
        created_at=response_ok.job.created_at,
    )
    await arq_dao.enqueue_task(response, user.username)
    worker_ = worker(functions=[work_ok])
    await worker_.main()
    assert await arq_dao.result(response.job.job_id, user.username) == "OK!"
    with test_client.websocket_connect(
        f"/jobs/{response.job.job_id}/ws"
    ) as websocket:
        data = websocket.receive_json()
        assert data == response_ok.model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_error(
    test_client: TestClient,
    user: User,
    arq_dao: ArqDAO,
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
    await arq_dao.enqueue_task(response, user.username)
    worker_ = worker(functions=[work_error])
    await worker_.main()
    with pytest.raises(ValueError):
        await arq_dao.result(response.job.job_id, user.username)
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


@pytest.mark.asyncio(scope="session")
async def test_job_cancelled(
    test_client: TestClient,
    user: User,
    arq_dao: ArqDAO,
    arq_redis: ArqRedis,
    worker: Callable[..., Worker],
    work_long: Function,
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)

    # отменяем до старта: задача поднимется из очереди, но отменится
    # до запуска функции
    cancel = asyncio.create_task(arq_dao.cancel_job(job_id, user.username))
    await wait_for_abort_request(arq_redis, job_id)

    worker_ = worker(functions=[work_long], allow_abort_jobs=True)
    await worker_.main()
    assert (await cancel).job.status is JobStatus.cancelled

    with test_client.websocket_connect(f"/jobs/{job_id}/ws") as websocket:
        data = websocket.receive_json()
        assert data["job"]["status"] == JobStatus.cancelled.value
        assert data["job"]["message"] == "Job is cancelled"


@pytest.mark.asyncio(scope="session")
async def test_websocket_status_then_cancel(
    test_client: TestClient,
    user: User,
    arq_redis: ArqRedis,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_long: Function,
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)

    worker_ = worker(functions=[work_long], burst=False, allow_abort_jobs=True)
    asyncio.create_task(worker_.async_run())
    await wait_for_job_start(arq_redis, job_id)

    with test_client.websocket_connect(f"/jobs/{job_id}/ws") as websocket:
        # первым приходит текущий статус — задача ещё выполняется
        first = websocket.receive_json()
        assert first["job"]["status"] == JobStatus.in_progress.value

        cancel = await arq_dao.cancel_job(job_id, user.username)
        assert cancel.job.status is JobStatus.cancelled

        # вторым — финальный статус отменённой задачи
        second = websocket.receive_json()
        assert second["job"]["status"] == JobStatus.cancelled.value
        assert second["job"]["message"] == "Job is cancelled"
