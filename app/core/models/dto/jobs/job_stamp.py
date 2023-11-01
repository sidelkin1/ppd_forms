from typing import Self
from uuid import uuid4

from arq.jobs import Job
from pydantic import BaseModel, ConfigDict, Field

from app.core.models.enums.job_status import JobStatus
from app.core.utils.result_path import result_name


class JobStamp(BaseModel):
    user_id: str | None = None
    message: str | None = None
    status: JobStatus = Field(default=JobStatus.created)
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    file_id: str | None = Field(default_factory=result_name)

    model_config = ConfigDict(extra="forbid")

    @classmethod
    async def from_job(cls, job: Job) -> Self:
        status = JobStatus.from_arq(await job.status())
        if status is JobStatus.not_found:
            return cls(job_id=job.job_id, file_id=None, status=status)
        info = await job.info()
        obj = cls(**info.args[1])  # TODO more robust way
        if status is JobStatus.in_progress:
            obj.status = JobStatus.in_progress
        elif info.success:
            obj.status = JobStatus.completed
        else:
            obj.status = JobStatus.execution_error
            obj.message = repr(info.result)
        return obj
