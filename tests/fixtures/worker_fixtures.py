import asyncio
from typing import Any

import pytest
from arq.worker import Function, func

from app.core.models.dto import TaskBase, UneftFieldDB, UneftReservoirDB
from app.core.models.schemas import BaseResponse


@pytest.fixture(scope="session")
def work_ok() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> str:
        return "OK!"

    return func(perform_work, name="work_ok")


@pytest.fixture(scope="session")
def work_error() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> None:
        raise ValueError("Error!")

    return func(perform_work, name="work_error")


@pytest.fixture(scope="session")
def work_long() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> None:
        await asyncio.sleep(3600)

    return func(perform_work, name="work_long")


@pytest.fixture(scope="session")
def work_uneft() -> Function:
    async def perform_work(
        ctx: dict[str, Any],
        response: BaseResponse[TaskBase],
        log_ctx: dict[str, Any],
    ) -> Any:
        result = {
            "uneft:fields": [
                UneftFieldDB(id=1, name="F1"),
                UneftFieldDB(id=2, name="F2"),
            ],
            "uneft:reservoirs": [
                UneftReservoirDB(id=1, name="R1"),
                UneftReservoirDB(id=2, name="R2"),
            ],
        }
        return result.get(response.task.route_url)

    return func(perform_work, name="perform_work")
