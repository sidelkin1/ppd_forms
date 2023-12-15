from typing import Any, Self

from arq.jobs import Job
from pydantic import ConfigDict, Field

from app.core.models.dto import JobStamp
from app.core.models.enums import JobStatus
from app.core.models.schemas.responses.base import BaseResponse
from app.core.models.schemas.responses.task import TaskResponse, TaskT


class JobResponse(BaseResponse[dict[str, Any]]):
    task: dict[str, Any] = Field(alias="data")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    async def from_job(cls, job: Job) -> Self:
        status = JobStatus.from_arq(await job.status())
        if status is JobStatus.not_found:
            data = None
            job_stamp = JobStamp(
                job_id=job.job_id, file_id=None, status=status
            )
        else:
            info = await job.info()
            response: TaskResponse[TaskT] = info.args[0]
            data = response.task.model_dump()
            job_stamp = response.job
            if status is JobStatus.in_progress:
                job_stamp.status = JobStatus.in_progress
            elif info.success:
                job_stamp.status = JobStatus.completed
            else:
                job_stamp.status = JobStatus.error
                job_stamp.message = str(info.result)
        return cls(data=data, job=job_stamp)
