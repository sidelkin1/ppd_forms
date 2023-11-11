from typing import TypeVar

from pydantic import ConfigDict, Field

from app.core.models.dto import TaskBase
from app.core.models.schemas.responses.base import BaseResponse

TaskT = TypeVar("TaskT", bound=TaskBase, covariant=True, contravariant=False)


class TaskResponse(BaseResponse[TaskT]):
    data: TaskT = Field(alias="task")

    model_config = ConfigDict(populate_by_name=True)
