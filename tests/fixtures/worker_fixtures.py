import asyncio
from typing import Any

import pytest
from arq.worker import Function, func

from app.api.models.responses import (
    BaseResponse,
    FieldsResponse,
    ReservoirsResponse,
)
from app.core.models.dto import TaskBase, UneftFieldDB, UneftReservoirDB


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
    fake_fields = {
        1: UneftFieldDB(id=1, name="F1"),
        2: UneftFieldDB(id=2, name="F2"),
    }
    fake_reservoirs = {
        1: [
            UneftReservoirDB(id=1, name="R1"),
            UneftReservoirDB(id=2, name="R2"),
        ],
        2: [UneftReservoirDB(id=1, name="R1")],
    }

    async def perform_work(
        ctx: dict[str, Any],
        response: FieldsResponse | ReservoirsResponse,
        log_ctx: dict[str, Any],
    ) -> Any:
        match (
            response.task.route_url,
            response.__class__.__name__,
            response.task.field_id,
        ):
            case "uneft:fields", FieldsResponse.__name__, None:
                return list(fake_fields.values())
            case ("uneft:fields", FieldsResponse.__name__, int() as field_id):
                return fake_fields.get(field_id, None)
            case (
                "uneft:reservoirs",
                ReservoirsResponse.__name__,
                int() as field_id,
            ):
                return fake_reservoirs.get(field_id, None)
        raise ValueError("Unknown job!")

    return func(perform_work, name="perform_work")
