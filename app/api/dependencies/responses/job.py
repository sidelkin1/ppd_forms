from typing import Annotated

from fastapi import Depends

from app.api.dependencies.job import CurrentJobDep
from app.core.models.schemas import JobResponse


def job_response_provider() -> JobResponse:
    raise NotImplementedError


async def get_job_response(job: CurrentJobDep) -> JobResponse:
    return await JobResponse.from_job(job)


JobResponseDep = Annotated[JobResponse, Depends(job_response_provider)]
