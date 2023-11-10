from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

from app.core.models.enums.task_id import TaskId


class TaskBase(BaseModel):
    _task_id: ClassVar[TaskId]
    _route_fields: ClassVar[list[str]]

    @computed_field
    @property
    def task_id(self) -> TaskId:
        return self._task_id

    @property
    def route_url(self) -> str:
        return ":".join(getattr(self, field) for field in self._route_fields)

    @model_validator(mode="before")
    @classmethod
    def exclude_task_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("task_id", None)
        return data

    def __init_subclass__(cls, /, task_id, route_fields, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._task_id = task_id
        cls._route_fields = route_fields

    model_config = ConfigDict(extra="forbid")
