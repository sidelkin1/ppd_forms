from typing import Annotated

import structlog
from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.auth import UserDep
from app.api.dependencies.redis import RedisDep
from app.core.models.dto import JobStamp


def get_new_job() -> JobStamp:
    raise NotImplementedError


def get_current_job() -> Job:
    raise NotImplementedError


class JobProvider:
    async def create(self, user: UserDep) -> JobStamp:
        job = JobStamp(user_id=user.username)
        structlog.contextvars.bind_contextvars(job_id=job.job_id)
        return job

    async def current(self, job_id: str, redis: RedisDep) -> Job:
        job = Job(job_id=job_id, redis=redis.redis)
        structlog.contextvars.bind_contextvars(job_id=job_id)
        return job


def get_job_provider() -> JobProvider:
    raise NotImplementedError


JobDep = Annotated[JobProvider, Depends(get_job_provider)]
NewJobDep = Annotated[JobStamp, Depends(get_new_job)]
CurrentJobDep = Annotated[Job, Depends(get_current_job)]
