from datetime import datetime

import pytest
from arq.connections import ArqRedis
from arq.jobs import Job, JobStatus
from fastapi import status
from httpx import AsyncClient

from app.core.models.dto import TaskDatabase


@pytest.mark.asyncio(scope="session")
async def test_load_database_success(
    client: AsyncClient, arq_redis: ArqRedis, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/{task_database.table.value}/{task_database.mode.value}",
        json={
            "date_from": task_database.date_from.isoformat(),
            "date_to": task_database.date_to.isoformat(),
        },
    )
    assert resp.is_success
    data = resp.json()
    assert data["task"] == task_database.model_dump(mode="json")
    job = Job(job_id=data["job"]["job_id"], redis=arq_redis)
    assert JobStatus.queued is await job.status()


@pytest.mark.asyncio(scope="session")
async def test_load_database_unknown_table(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/unknown/{task_database.mode.value}",
        json={
            "date_from": task_database.date_from.isoformat(),
            "date_to": task_database.date_to.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_unknown_mode(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/{task_database.table.value}/unknown",
        json={
            "date_from": task_database.date_from.isoformat(),
            "date_to": task_database.date_to.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_no_dates(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/{task_database.table.value}/{task_database.mode.value}"
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_dates_not_ordered(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/{task_database.table.value}/{task_database.mode.value}",
        json={
            "date_from": task_database.date_to.isoformat(),
            "date_to": task_database.date_from.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_load_database_dates_wrong_format(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        f"database/{task_database.table.value}/{task_database.mode.value}",
        json={
            "date_from": datetime.now().isoformat(),
            "date_to": datetime.now().isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_reload_profile_not_allowed(
    client: AsyncClient, task_database: TaskDatabase
):
    resp = await client.post(
        "database/profile/reload",
        json={
            "date_from": task_database.date_from.isoformat(),
            "date_to": task_database.date_to.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.asyncio(scope="session")
async def test_get_dates(client: AsyncClient):
    resp = await client.get("database/profile")
    assert resp.is_success
    data = resp.json()
    assert data == {"min_date": "1996-10-15", "max_date": "2003-09-29"}
