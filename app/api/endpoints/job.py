import logging

from fastapi import APIRouter, WebSocket
from fastapi_pagination import Page, paginate

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import JobResponseDep
from app.api.dependencies.redis import RedisDep
from app.api.dependencies.tracker import JobTrackerDep
from app.api.models.responses import JobResponse
from app.core.models.enums.task_id import TaskId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "/scheduled",
    response_model=Page[JobResponse],
    response_model_exclude_none=True,
)
async def get_user_tasks(
    redis: RedisDep, user: UserDep, task_id: TaskId | None = None
):
    tasks = await redis.get_scheduled_tasks(user.username, task_id)
    return paginate(tasks)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    response_model_exclude_none=True,
)
async def get_job_status(job_id: str, user: UserDep, response: JobResponseDep):
    logger.debug(
        "Current job", extra={"task": response.task, "job": response.job}
    )
    return response


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    job_id: str,
    user: UserDep,
    response: JobResponseDep,
    tracker: JobTrackerDep,
):
    logger.debug(
        "Current job", extra={"task": response.task, "job": response.job}
    )
    async with tracker:
        await tracker.status()
