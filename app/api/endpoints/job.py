from fastapi import APIRouter

from app.api.dependencies.job import CurrentJobDep
from app.core.models.dto import JobStamp

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobStamp,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, job_stamp: CurrentJobDep):
    return job_stamp
