from typing import Annotated

from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.user.session import UserIdDep
from app.core.models.schemas import JobResponse


def job_response_provider() -> JobResponse:
    raise NotImplementedError


async def get_job_response(
    user_id: UserIdDep, job_id: str, redis: RedisDep
) -> JobResponse:
    job = Job(job_id=job_id, redis=redis.redis)
    return await JobResponse.from_job(job)


JobResponseDep = Annotated[JobResponse, Depends(job_response_provider)]
