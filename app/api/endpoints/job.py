from fastapi import APIRouter, WebSocket

from app.api.dependencies.job import JobResponseDep, JobTrackerDep
from app.api.dependencies.user.session import UserIdDep
from app.core.models.schemas import JobResponse

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(
    job_id: str, user_id: UserIdDep, response: JobResponseDep
):
    return response


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    job_id: str,
    user_id: UserIdDep,
    tracker: JobTrackerDep,
):
    await tracker.status()
