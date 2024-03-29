import logging

from fastapi import APIRouter, WebSocket

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import CurrentJobDep
from app.api.utils.tracker import JobTracker
from app.core.models.schemas import JobResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, user: UserDep, job: CurrentJobDep):
    response = await JobResponse.from_job(job)
    logger.debug("Current job", extra={"job": response})
    return response


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, job_id: str, user: UserDep, job: CurrentJobDep
):
    response = await JobResponse.from_job(job)
    logger.debug("Current job", extra={"job": response})
    async with JobTracker(websocket, job, response) as tracker:
        await tracker.status()
