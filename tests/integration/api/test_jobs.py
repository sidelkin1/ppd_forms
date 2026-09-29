import asyncio
from collections.abc import Callable, Iterator

import pytest
from arq.connections import ArqRedis
from arq.constants import (
    abort_jobs_ss,
    default_queue_name,
    job_key_prefix,
    result_key_prefix,
)
from arq.worker import Function, Worker
from fastapi import FastAPI, status
from httpx import AsyncClient

from app.api.dependencies.redis import RedisProvider, redis_provider
from app.api.models.auth import User
from app.core.config.models.app import AppSettings
from app.core.models.enums import JobStatus
from app.infrastructure.redis.config.models.redis import RedisSettings
from app.infrastructure.redis.dao.arq import ArqDAO
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from tests.integration.api.waiters import (
    wait_for_abort_request,
    wait_for_job_start,
)
from tests.mocks.responses import TaskTestResponse

FAST_ABORT_TIMEOUT = 0.01


@pytest.fixture
def fast_abort(
    app: FastAPI, redis_config: RedisSettings, app_config: AppSettings
) -> Iterator[None]:
    """Сократить abort_timeout, чтобы 202 наступал за доли секунды."""
    original = app.dependency_overrides[redis_provider]
    app.dependency_overrides[redis_provider] = RedisProvider(
        pool=create_redis_pool(redis_config),
        expires=app_config.keep_result,
        abort_timeout=FAST_ABORT_TIMEOUT,
    ).dao
    yield
    app.dependency_overrides[redis_provider] = original


@pytest.mark.asyncio(scope="session")
async def test_job_ok(
    client: AsyncClient,
    user: User,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response_ok = TaskTestResponse.test(status=JobStatus.completed)
    response_ok.result = "OK!"
    response = TaskTestResponse.test(
        job_id=response_ok.job.job_id, created_at=response_ok.job.created_at
    )
    await arq_dao.enqueue_task(response, user.username)
    worker_ = worker(functions=[work_ok])
    await worker_.main()
    assert await arq_dao.result(response.job.job_id, user.username) == "OK!"
    resp = await client.get(f"/jobs/{response.job.job_id}")
    assert resp.is_success
    data = resp.json()
    assert data == response_ok.model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_error(
    client: AsyncClient,
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
    resp = await client.get(f"/jobs/{response.job.job_id}")
    assert resp.is_success
    data = resp.json()
    assert data == response_error.model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio(scope="session")
async def test_job_is_not_found(client: AsyncClient):
    job_id = "unknown_job_id"
    resp = await client.get(f"/jobs/{job_id}")
    assert resp.is_success
    data = resp.json()
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
async def test_job_is_cancelled(
    client: AsyncClient,
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

    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.is_success
    data = resp.json()
    assert data["job"]["status"] == JobStatus.cancelled.value
    assert data["job"]["message"] == "Job is cancelled"

    resp = await client.get(f"/jobs/{job_id}")
    assert resp.json()["job"]["status"] == JobStatus.cancelled.value

    # отмена идемпотентна: повторный запрос — снова 200 cancelled,
    # а не 404 «already finished»
    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.is_success
    assert resp.json()["job"]["status"] == JobStatus.cancelled.value


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_before_start(
    client: AsyncClient,
    user: User,
    arq_redis: ArqRedis,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_long: Function,
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)

    # задача поднимется из очереди, но отменится до запуска функции
    cancel = asyncio.create_task(client.post(f"/jobs/{job_id}/cancel"))
    await wait_for_abort_request(arq_redis, job_id)

    worker_ = worker(functions=[work_long], allow_abort_jobs=True)
    await worker_.main()

    resp = await cancel
    assert resp.is_success
    assert resp.json()["job"]["status"] == JobStatus.cancelled.value


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_is_finished(
    client: AsyncClient,
    user: User,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_ok: Function,
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)
    worker_ = worker(functions=[work_ok])
    await worker_.main()
    assert await arq_dao.result(job_id, user.username) == "OK!"

    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == status.HTTP_409_CONFLICT
    assert resp.json()["detail"] == "Job is already finished"

    # состояние задачи остаётся доступным, чтобы UI обновил строку
    resp = await client.get(f"/jobs/{job_id}")
    assert resp.json()["job"]["status"] == JobStatus.completed.value
    assert resp.json()["result"] == "OK!"


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_is_not_found(client: AsyncClient):
    resp = await client.post("/jobs/unknown_job_id/cancel")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Job is not found"


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_is_failed(
    client: AsyncClient,
    user: User,
    arq_dao: ArqDAO,
    worker: Callable[..., Worker],
    work_error: Function,
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)
    worker_ = worker(functions=[work_error])
    await worker_.main()
    with pytest.raises(ValueError):
        await arq_dao.result(job_id, user.username)

    # задача уже упала — отменять нечего, состояние отдаём как есть
    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == status.HTTP_409_CONFLICT
    assert resp.json()["detail"] == "Job is already finished"

    # при этом состояние задачи по-прежнему доступно клиенту
    resp = await client.get(f"/jobs/{job_id}")
    assert resp.json()["job"]["status"] == JobStatus.error.value
    assert resp.json()["job"]["message"] == "Error!"


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_lost_execution(
    client: AsyncClient, user: User, arq_redis: ArqRedis, arq_dao: ArqDAO
):
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)

    # запись об исполнении потеряна: перезапуск Redis или истёк keep_result
    await arq_redis.delete(job_key_prefix + job_id, result_key_prefix + job_id)
    await arq_redis.zrem(default_queue_name, job_id)

    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Job is not found"


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_foreign_job(client: AsyncClient, arq_dao: ArqDAO):
    # задача стоит в расписании другого пользователя — отменять её нельзя
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, "another_user")

    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Job is not found"


@pytest.mark.asyncio(scope="session")
async def test_job_cancel_pending(
    client: AsyncClient,
    user: User,
    arq_redis: ArqRedis,
    arq_dao: ArqDAO,
    fast_abort: None,
):
    # задача в очереди, воркера нет — отмена принята, но не подтверждена
    response = TaskTestResponse.test()
    job_id = response.job.job_id
    await arq_dao.enqueue_task(response, user.username)

    resp = await client.post(f"/jobs/{job_id}/cancel")
    assert resp.status_code == status.HTTP_202_ACCEPTED
    assert resp.json()["detail"] == "Job cancellation is pending"

    # маркер отмены остался — сработает, когда появится воркер
    assert await arq_redis.zscore(abort_jobs_ss, job_id) is not None

    # состояние по-прежнему in_progress
    resp = await client.get(f"/jobs/{job_id}")
    assert resp.json()["job"]["status"] == JobStatus.in_progress.value
