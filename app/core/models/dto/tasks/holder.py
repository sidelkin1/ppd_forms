from typing import Any

from app.core.models.dto.tasks.base import TaskBase
from app.core.models.enums.task_id import TaskId


class TaskHolderDTO:
    def __init__(self) -> None:
        self.registry: dict[TaskId, type[TaskBase]] = {}

    def add(self, model: type[TaskBase]) -> type[TaskBase]:
        self.registry[model._task_id] = model
        return model

    def to_dto(self, data: dict[str, Any]) -> TaskBase:
        task_id = TaskId[data.pop("task_id")]
        return self.registry[task_id](**data)
