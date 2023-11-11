from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.core.models.enums import JobStatus
from app.core.utils.result_path import result_name


class JobStamp(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    file_id: str | None = Field(default_factory=result_name)
    user_id: str | None = None
    message: str | None = None
    status: JobStatus = JobStatus.created

    model_config = ConfigDict(extra="forbid")
