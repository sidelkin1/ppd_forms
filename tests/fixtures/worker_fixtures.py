import asyncio
from typing import Any, cast

import pytest
from arq.worker import Function, func

from app.api.models.responses import (
    BaseResponse,
    FieldsResponse,
    ReservoirsResponse,
)
from app.core.models.dto import TaskBase
from app.core.services.uneft import uneft_fields, uneft_reservoirs
from app.infrastructure.holder import HolderDAO


@pytest.fixture
def work_ok() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> str:
        return "OK!"

    return func(perform_work, name="work_ok")


@pytest.fixture
def work_error() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> None:
        raise ValueError("Error!")

    return func(perform_work, name="work_error")


@pytest.fixture
def work_long() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: BaseResponse[TaskBase]
    ) -> None:
        await asyncio.sleep(3600)

    return func(perform_work, name="work_long")


@pytest.fixture
def work_uneft(holder: HolderDAO) -> Function:
    async def perform_work(
        ctx: dict[str, Any],
        response: FieldsResponse | ReservoirsResponse,
        log_ctx: dict[str, Any],
    ) -> Any:
        match response.task.route_url:
            case "uneft:fields":
                response = cast(FieldsResponse, response)
                return await uneft_fields(
                    response.task.stock, response.task.field_id, holder.uneft
                )
            case "uneft:reservoirs":
                response = cast(ReservoirsResponse, response)
                return await uneft_reservoirs(
                    response.task.field_id, holder.uneft
                )
        raise ValueError("Unknown job!")

    return func(perform_work, name="perform_work")
