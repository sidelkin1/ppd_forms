from typing import Annotated

import structlog
from fastapi import Depends

from app.api.dependencies.auth import UserDep
from app.core.models.dto import JobStamp


def get_new_job() -> JobStamp:
    raise NotImplementedError


def create_job_stamp(user: UserDep) -> JobStamp:
    job = JobStamp(user_id=user.username)
    structlog.contextvars.bind_contextvars(job_id=job.job_id)
    return job


NewJobDep = Annotated[JobStamp, Depends(get_new_job)]
