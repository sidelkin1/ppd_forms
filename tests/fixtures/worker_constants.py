import asyncio
from typing import Any

from app.core.models.schemas import TaskResponse


async def work_ok(ctx: dict[str, Any], response: TaskResponse) -> None:
    print("OK!")


async def work_error(ctx: dict[str, Any], response: TaskResponse) -> None:
    raise ValueError("Error!")


async def work_long(ctx: dict[str, Any], response: TaskResponse) -> None:
    await asyncio.sleep(3600)
