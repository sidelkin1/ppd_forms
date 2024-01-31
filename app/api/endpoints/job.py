from arq.jobs import Job
from fastapi import APIRouter, WebSocket

from app.api.dependencies.redis import RedisDep
from app.api.utils.tracker import JobTracker
from app.core.models.schemas import JobResponse

router = APIRouter()


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, redis: RedisDep):
    current_job = Job(job_id=job_id, redis=redis.redis)
    response = await JobResponse.from_job(current_job)
    return response


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket, job_id: str, redis: RedisDep
):
    current_job = Job(job_id=job_id, redis=redis.redis)
    response = await JobResponse.from_job(current_job)
    async with JobTracker(websocket, current_job, response) as tracker:
        await tracker.status()
