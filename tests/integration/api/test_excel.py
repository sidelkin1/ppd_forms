import pytest
from arq.connections import ArqRedis
from arq.jobs import Job, JobStatus
from fastapi import status
from httpx import AsyncClient

from app.core.models.dto import TaskExcel


@pytest.mark.asyncio(scope="session")
async def test_load_database_success(
    client: AsyncClient, arq_redis: ArqRedis, task_excel: TaskExcel
):
    resp = await client.post(
        f"excel/{task_excel.table.value}/{task_excel.mode.value}",
        json={"file": "test.xlsx"},
    )
    assert resp.is_success
    data = resp.json()
    assert data["task"] == task_excel.model_dump(mode="json")
    job = Job(job_id=data["job"]["job_id"], redis=arq_redis)
    assert JobStatus.queued is await job.status()


@pytest.mark.asyncio(scope="session")
async def test_load_database_unknown_table(
    client: AsyncClient, task_excel: TaskExcel
):
    resp = await client.post(
        f"excel/unknown/{task_excel.mode.value}",
        json={"file": "test.xlsx"},
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_unknown_mode(
    client: AsyncClient, task_excel: TaskExcel
):
    resp = await client.post(
        f"excel/{task_excel.table.value}/unknown",
        json={"file": "test.xlsx"},
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_no_path(
    client: AsyncClient, task_excel: TaskExcel
):
    resp = await client.post(
        f"excel/{task_excel.table.value}/{task_excel.mode.value}"
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("table", ["ns_ppd", "ns_oil"])
@pytest.mark.asyncio(scope="session")
async def test_get_dates(client: AsyncClient, table: str):
    resp = await client.get(f"excel/{table}")
    assert resp.is_success
    data = resp.json()
    assert data == {"min_date": "2000-01-01", "max_date": "2001-01-01"}
