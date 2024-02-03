from datetime import datetime

import pytest
from arq.connections import ArqRedis
from arq.jobs import Job, JobStatus
from fastapi import status
from httpx import AsyncClient

from app.core.models.dto import TaskOilLoss, TaskReport


def get_correct_url(task: TaskReport | TaskOilLoss) -> str:
    if isinstance(task, TaskOilLoss):
        return f"/reports/{task.name.value}/{task.mode.value}"
    return f"/reports/{task.name.value}"


def get_unknown_name_url(task: TaskReport | TaskOilLoss) -> str:
    if isinstance(task, TaskOilLoss):
        return f"/reports/{task.name.value}/unknown"
    return "/reports/unknown"


@pytest.mark.parametrize("task", ["task_report", "task_oil_loss"])
@pytest.mark.asyncio(scope="session")
async def test_generate_report_success(
    client: AsyncClient, arq_redis: ArqRedis, task: str, request
):
    task_report: TaskReport | TaskOilLoss = request.getfixturevalue(task)
    resp = await client.post(
        get_correct_url(task_report),
        json={
            "date_from": task_report.date_from.isoformat(),
            "date_to": task_report.date_to.isoformat(),
        },
    )
    assert resp.is_success
    data = resp.json()
    assert data["task"] == task_report.model_dump(mode="json")
    job = Job(job_id=data["job"]["job_id"], redis=arq_redis)
    assert JobStatus.queued is await job.status()


@pytest.mark.parametrize("task", ["task_report", "task_oil_loss"])
@pytest.mark.asyncio(scope="session")
async def test_generate_report_unknown_name(
    client: AsyncClient, task: str, request
):
    task_report: TaskReport | TaskOilLoss = request.getfixturevalue(task)
    resp = await client.post(
        get_unknown_name_url(task_report),
        json={
            "date_from": task_report.date_from.isoformat(),
            "date_to": task_report.date_to.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("task", ["task_report", "task_oil_loss"])
@pytest.mark.asyncio(scope="session")
async def test_generate_report_no_dates(
    client: AsyncClient, task: str, request
):
    task_report: TaskReport | TaskOilLoss = request.getfixturevalue(task)
    resp = await client.post(get_correct_url(task_report))
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("task", ["task_report", "task_oil_loss"])
@pytest.mark.asyncio(scope="session")
async def test_generate_report_dates_not_ordered(
    client: AsyncClient, task: str, request
):
    task_report: TaskReport | TaskOilLoss = request.getfixturevalue(task)
    resp = await client.post(
        get_correct_url(task_report),
        json={
            "date_from": task_report.date_to.isoformat(),
            "date_to": task_report.date_from.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("task", ["task_report", "task_oil_loss"])
@pytest.mark.asyncio(scope="session")
async def test_generate_report_dates_wrong_format(
    client: AsyncClient, task: str, request
):
    task_report: TaskReport | TaskOilLoss = request.getfixturevalue(task)
    resp = await client.post(
        get_correct_url(task_report),
        json={
            "date_from": datetime.now().isoformat(),
            "date_to": datetime.now().isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope="session")
async def test_generate_oil_loss_report_unknown_mode(
    client: AsyncClient, task_oil_loss: TaskOilLoss
):
    resp = await client.post(
        f"/reports/{task_oil_loss.name.value}/unknown",
        json={
            "date_from": task_oil_loss.date_from.isoformat(),
            "date_to": task_oil_loss.date_to.isoformat(),
        },
    )
    assert not resp.is_success
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
