import pytest
from arq.connections import ArqRedis
from httpx import AsyncClient

from app.api.models.auth import User
from app.core.config.models.app import AppSettings
from app.infrastructure.redis.dao.arq import ArqDAO
from tests.mocks.responses import TaskTestResponse


@pytest.fixture
def arq_dao(arq_redis: ArqRedis, app_config: AppSettings):
    return ArqDAO(arq_redis, app_config.keep_result)


@pytest.mark.asyncio
async def test_default_pagination(
    client: AsyncClient, user: User, arq_dao: ArqDAO
):
    responses = [
        TaskTestResponse.test(),
        TaskTestResponse.foo(),
        TaskTestResponse.bar(),
    ]
    for response in responses:
        await arq_dao.enqueue_task(response, user.username)
    resp = await client.get("/jobs/scheduled")
    assert resp.status_code == 200
    data = resp.json()
    for field in ["items", "pages", "page", "size", "total"]:
        assert field in data
    assert data["pages"] == 1
    assert data["page"] == 1
    assert data["size"] == 50
    assert data["total"] == len(responses)


@pytest.mark.asyncio
async def test_custom_page_size(
    client: AsyncClient, user: User, arq_dao: ArqDAO
):
    responses = [
        TaskTestResponse.test(),
        TaskTestResponse.foo(),
        TaskTestResponse.bar(),
    ]
    for response in responses:
        await arq_dao.enqueue_task(response, user.username)
    params = {"page": 1, "size": 1}
    resp = await client.get("/jobs/scheduled", params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_page_number_out_of_range(
    client: AsyncClient, user: User, arq_dao: ArqDAO
):
    responses = [
        TaskTestResponse.test(),
        TaskTestResponse.foo(),
        TaskTestResponse.bar(),
    ]
    for response in responses:
        await arq_dao.enqueue_task(response, user.username)
    params = {"page": 100, "size": 10}
    resp = await client.get("/jobs/scheduled", params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_tasks_no_filter(
    client: AsyncClient, user: User, arq_dao: ArqDAO
):
    responses = [
        TaskTestResponse.test(),
        TaskTestResponse.foo(),
        TaskTestResponse.bar(),
    ]
    usernames = [user.username, user.username, "test_user2"]
    for response, username in zip(responses, usernames):
        await arq_dao.enqueue_task(response, username)
    resp = await client.get("/jobs/scheduled")
    assert resp.status_code == 200
    data = resp.json()["items"]
    assert len(data) == 2
    assert responses[0].model_dump(mode="json", exclude_none=True) in data
    assert responses[1].model_dump(mode="json", exclude_none=True) in data


@pytest.mark.asyncio
async def test_get_tasks_with_filter(
    client: AsyncClient, user: User, arq_dao: ArqDAO
):
    responses = [
        TaskTestResponse.test(),
        TaskTestResponse.foo(),
        TaskTestResponse.bar(),
    ]
    for response in responses:
        await arq_dao.enqueue_task(response, user.username)
    resp = await client.get(
        f"/jobs/scheduled?task_id={responses[0].task.task_id.value}"
    )
    assert resp.status_code == 200
    data = resp.json()["items"]
    assert len(data) == 1
    assert data[0] == responses[0].model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio
async def test_get_tasks_no_tasks(
    client: AsyncClient,
    arq_dao: ArqDAO,  # to flush Redis
):
    resp = await client.get("/jobs/scheduled")
    assert resp.status_code == 200
    assert resp.json()["items"] == []


@pytest.mark.asyncio
async def test_get_tasks_invalid_task_id(client: AsyncClient):
    resp = await client.get("/jobs/scheduled?task_id=INVALID_TASK")
    assert resp.status_code == 422
