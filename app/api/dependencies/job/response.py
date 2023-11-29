from typing import Annotated

from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.job import CurrentJobDep
from app.api.dependencies.user.session import UserIdDep
from app.core.models.schemas import JobResponse


def job_response_provider() -> JobResponse:
    raise NotImplementedError


async def get_job_response(user_id: UserIdDep, job: CurrentJobDep) -> Job:
    return await JobResponse.from_job(job)


JobResponseDep = Annotated[JobResponse, Depends(job_response_provider)]
