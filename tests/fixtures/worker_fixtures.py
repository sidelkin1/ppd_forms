import asyncio
from typing import Any

import pytest
from arq.worker import Function, func

from app.core.models.schemas import TaskResponse


@pytest.fixture(scope="session")
def work_ok() -> Function:
    async def perform_work(ctx: dict[str, Any], response: TaskResponse) -> str:
        return "OK!"

    return func(perform_work, name="work_ok")


@pytest.fixture(scope="session")
def work_error() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: TaskResponse
    ) -> None:
        raise ValueError("Error!")

    return func(perform_work, name="work_error")


@pytest.fixture(scope="session")
def work_long() -> Function:
    async def perform_work(
        ctx: dict[str, Any], response: TaskResponse
    ) -> None:
        await asyncio.sleep(3600)

    return func(perform_work, name="work_long")
