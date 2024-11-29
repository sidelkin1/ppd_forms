from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

from app.core.models.enums import JobStatus

RESULT_SUFFIX_LENGTH = 8


class JobStamp(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    user_id: str | None = None
    message: str | None = None
    status: JobStatus = JobStatus.created
    created_at: datetime = Field(default_factory=datetime.now)

    @computed_field  # type: ignore[misc]
    @property
    def file_id(self) -> str | None:
        return "result_{}_{}".format(
            self.created_at.strftime("%Y_%m_%dT%H_%M_%S"),
            self.job_id[:RESULT_SUFFIX_LENGTH],
        )

    @model_validator(mode="before")
    @classmethod
    def exclude_file_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data.pop("file_id", None)
        return data

    model_config = ConfigDict(extra="forbid")
