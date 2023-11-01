from typing import Annotated

from fastapi import Depends

from app.api.dependencies.user.session import UserIdDep
from app.core.models.dto.jobs.job_stamp import JobStamp


def new_job_provider() -> JobStamp:
    raise NotImplementedError


async def create_job_stamp(user_id: UserIdDep) -> JobStamp:
    return JobStamp(user_id=user_id)


NewJobDep = Annotated[JobStamp, Depends(new_job_provider)]
