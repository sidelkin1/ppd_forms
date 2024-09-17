from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.core.models.enums import JobStatus


class JobStamp(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    file_id: str | None = Field(
        default_factory=lambda: datetime.now().strftime(
            "result_%Y_%m_%dT%H_%M_%S"
        )
    )
    user_id: str | None = None
    message: str | None = None
    status: JobStatus = JobStatus.created
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(extra="forbid")
