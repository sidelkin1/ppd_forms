from typing import Annotated

from fastapi import Depends

from app.api.dependencies.auth import UserDep
from app.core.models.dto import JobStamp


def new_job_provider() -> JobStamp:
    raise NotImplementedError


async def create_job_stamp(user: UserDep) -> JobStamp:
    return JobStamp(user_id=user.username)


NewJobDep = Annotated[JobStamp, Depends(new_job_provider)]
