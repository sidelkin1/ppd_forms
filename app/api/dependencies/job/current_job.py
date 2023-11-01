from typing import Annotated

from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.user.session import UserIdDep
from app.core.models.dto.jobs.job_stamp import JobStamp


def current_job_provider() -> JobStamp:
    raise NotImplementedError


async def get_job_stamp(
    user_id: UserIdDep, job_id: str, redis: RedisDep
) -> JobStamp:
    job = Job(job_id=job_id, redis=redis.redis)
    return await JobStamp.from_job(job)


CurrentJobDep = Annotated[JobStamp, Depends(current_job_provider)]
