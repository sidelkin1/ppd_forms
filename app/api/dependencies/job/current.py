from typing import Annotated

from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.redis.provider import RedisDep
from app.core.models.dto.jobs.job_stamp import JobStamp


def current_job_provider() -> JobStamp:
    raise NotImplementedError


async def get_current_job(job_id: str, redis: RedisDep) -> Job:
    return Job(job_id=job_id, redis=redis.redis)


CurrentJobDep = Annotated[Job, Depends(current_job_provider)]
