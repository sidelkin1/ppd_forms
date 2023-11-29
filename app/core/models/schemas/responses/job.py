from typing import Any, Self

from arq.jobs import Job

from app.core.models.dto import JobStamp
from app.core.models.enums import JobStatus
from app.core.models.schemas.responses.base import BaseResponse


class JobResponse(BaseResponse[dict[str, Any]]):
    @classmethod
    async def from_job(cls, job: Job) -> Self:
        status = JobStatus.from_arq(await job.status())
        if status is JobStatus.not_found:
            data = {}
            job_stamp = JobStamp(
                job_id=job.job_id, file_id=None, status=status
            )
        else:
            info = await job.info()
            data = dict(info.args[0])
            job_stamp = info.args[1]
            if status is JobStatus.in_progress:
                job_stamp.status = JobStatus.in_progress
            elif info.success:
                job_stamp.status = JobStatus.completed
            else:
                job_stamp.status = JobStatus.error
                job_stamp.message = str(info.result)
        return cls(data=data, job=job_stamp)
