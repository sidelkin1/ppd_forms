from typing import Any, Self, cast

from arq.jobs import Job, JobResult

from app.api.models.responses.base import BaseResponse
from app.core.models.dto import JobStamp, TaskBase
from app.core.models.enums import JobStatus


class JobResponse(BaseResponse[dict[str, Any] | None]):
    @classmethod
    async def from_job(cls, job: Job) -> Self:
        status = JobStatus.from_arq(await job.status())
        if status is JobStatus.not_found:
            task = None
            job_stamp = JobStamp(
                job_id=job.job_id, file_id=None, status=status
            )
        else:
            info = cast(JobResult, await job.info())
            response: BaseResponse[TaskBase] = info.args[0]
            task = response.task.model_dump()
            job_stamp = response.job
            if status is JobStatus.in_progress:
                job_stamp.status = JobStatus.in_progress
            elif info.success:
                job_stamp.status = JobStatus.completed
            else:
                job_stamp.status = JobStatus.error
                job_stamp.message = str(info.result)
        return cls(task=task, job=job_stamp)
