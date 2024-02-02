from fastapi import APIRouter, WebSocket

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import JobTrackerDep
from app.api.dependencies.responses import JobResponseDep
from app.core.models.schemas import JobResponse

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, user: UserDep, response: JobResponseDep):
    return response


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, job_id: str, tracker: JobTrackerDep
):
    await tracker.status()
