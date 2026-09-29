from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from app.core.models.dto.jobs.job_stamp import JobStamp

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    task: T
    job: JobStamp
    result: Any = None

    model_config = ConfigDict(extra="forbid")
