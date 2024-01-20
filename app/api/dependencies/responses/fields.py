from typing import Annotated

from fastapi import Depends

from app.api.dependencies.user import UserIdDep
from app.core.models.dto import JobStamp, TaskFields
from app.core.models.enums import UneftAssets
from app.core.models.schemas import FieldsResponse


def task_fields_provider() -> FieldsResponse:
    raise NotImplementedError


async def get_fields(user_id: UserIdDep) -> FieldsResponse:
    task = TaskFields(assets=UneftAssets.fields)
    return FieldsResponse(task=task, job=JobStamp(user_id=user_id))


FieldsResponseDep = Annotated[FieldsResponse, Depends(task_fields_provider)]
