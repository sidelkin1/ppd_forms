from fastapi import APIRouter, HTTPException, status

from app.api.dependencies.dao.provider import HolderDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.tasks import TaskDatabaseDep
from app.api.dependencies.user import UserDirDep
from app.api.endpoints.websocket import websocket_endpoint
from app.core.models.dto import TaskDatabase
from app.core.models.enums import LoadMode, OfmTableName
from app.core.models.schemas import DateRange, TaskResponse
from app.core.services.date_range import date_range

router = APIRouter()


@router.post("/profile/reload", deprecated=True)
async def reload_profile():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Данная операция недопустима!",
    )


@router.post(
    "/{table}/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse[TaskDatabase],
    response_model_exclude_none=True,
)
async def load_database(
    table: OfmTableName,
    mode: LoadMode,
    date_range: DateRange,
    task: TaskDatabaseDep,
    redis: RedisDep,
    job_stamp: NewJobDep,
    directory: UserDirDep,
):
    await redis.enqueue_task(task, job_stamp)
    return TaskResponse[TaskDatabase](task=task, job=job_stamp)


@router.get("/{table}")
async def get_dates(table: OfmTableName, holder: HolderDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}


router.add_api_websocket_route("/ws", websocket_endpoint)
