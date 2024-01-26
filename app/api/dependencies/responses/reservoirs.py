from typing import Annotated

from fastapi import Depends

from app.api.dependencies.settings import SettingsDep
from app.api.dependencies.user import UserIdDep
from app.core.models.dto import JobStamp, TaskReservoirs
from app.core.models.enums import UneftAssets
from app.core.models.schemas import ReservoirsResponse


def task_reservoirs_provider() -> ReservoirsResponse:
    raise NotImplementedError


async def get_reservoirs(
    field_id: int,
    user_id: UserIdDep,
    settings: SettingsDep,
) -> ReservoirsResponse:
    task = TaskReservoirs(assets=UneftAssets.reservoirs, field_id=field_id)
    return ReservoirsResponse(
        _file_dir=settings.file_dir, task=task, job=JobStamp(user_id=user_id)
    )


ReservoirsResponseDep = Annotated[
    ReservoirsResponse, Depends(task_reservoirs_provider)
]
