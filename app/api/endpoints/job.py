from fastapi import APIRouter

from app.api.dependencies.job import JobResponseDep
from app.core.models.schemas import JobResponse

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, response: JobResponseDep):
    return response
