from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from app.core.models.dto import JobStamp, TaskBase

TaskT = TypeVar(
    "TaskT",
    bound=TaskBase | dict[str, Any],
    covariant=True,
    contravariant=False,
)


class TaskResponse(BaseModel, Generic[TaskT]):
    task: TaskT
    job: JobStamp

    model_config = ConfigDict(extra="forbid")
