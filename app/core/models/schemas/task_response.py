from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from app.core.models.dto import JobStamp, TaskBase

TaskT = TypeVar("TaskT", bound=TaskBase, covariant=True, contravariant=False)


class TaskResponse(BaseModel, Generic[TaskT]):
    task: TaskT | dict[str, Any]
    job: JobStamp

    model_config = ConfigDict(extra="forbid")
