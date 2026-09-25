import logging

from fastapi import APIRouter, HTTPException, WebSocket, status
from fastapi_pagination import Page, paginate

from app.api.dependencies.auth import UserDep
from app.api.dependencies.redis import RedisDep
from app.api.dependencies.tracker import JobTrackerDep
from app.core.models.dto import JobResponse
from app.core.models.enums import JobStatus
from app.core.models.enums.task_id import TaskId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

JOB_NOT_FOUND_DETAIL = "Job is not found"
JOB_ALREADY_FINISHED_DETAIL = "Job is already finished"
JOB_CANCEL_PENDING_DETAIL = "Job cancellation is pending"


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
async def get_job_status(job_id: str, redis: RedisDep, user: UserDep):
    response = await redis.response(job_id, user.username)
    logger.debug(
        "Current job", extra={"task": response.task, "job": response.job}
    )
    return response


@router.post(
    "/{job_id}/cancel",
    response_model=JobResponse,
    response_model_exclude_none=True,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": JOB_NOT_FOUND_DETAIL,
            "content": {
                "application/json": {
                    "example": {"detail": JOB_NOT_FOUND_DETAIL}
                }
            },
        },
        status.HTTP_202_ACCEPTED: {
            "description": JOB_CANCEL_PENDING_DETAIL,
            "content": {
                "application/json": {
                    "example": {"detail": JOB_CANCEL_PENDING_DETAIL}
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "description": JOB_ALREADY_FINISHED_DETAIL,
            "content": {
                "application/json": {
                    "example": {"detail": JOB_ALREADY_FINISHED_DETAIL}
                }
            },
        },
    },
)
async def cancel_job(job_id: str, user: UserDep, redis: RedisDep):
    response = await redis.cancel_job(job_id, user.username)
    # 200 только если итоговое состояние — cancelled: задача отменена сейчас
    # или была отменена раньше (отмена идемпотентна)
    if response.job.status is JobStatus.not_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=JOB_NOT_FOUND_DETAIL,
        )
    if response.job.status is JobStatus.cancelled:
        return response
    if response.job.status is JobStatus.in_progress:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail=JOB_CANCEL_PENDING_DETAIL,
        )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=JOB_ALREADY_FINISHED_DETAIL,
    )


@router.websocket("/{job_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    job_id: str,
    redis: RedisDep,
    user: UserDep,
    tracker: JobTrackerDep,
):
    response = await redis.response(job_id, user.username)
    logger.debug(
        "Current job", extra={"task": response.task, "job": response.job}
    )
    async with tracker:
        await tracker.status()
