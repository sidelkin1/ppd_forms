from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from app.core.models.dto import JobStamp

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    task: T | None = None
    job: JobStamp

    model_config = ConfigDict(extra="forbid")
