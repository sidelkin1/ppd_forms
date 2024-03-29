from fastapi import APIRouter, HTTPException, status

from app.api.dependencies.auth import UserDep
from app.api.dependencies.db import HolderDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.redis import RedisDep
from app.core.models.dto import TaskDatabase
from app.core.models.enums import LoadMode, OfmTableName
from app.core.models.schemas import DatabaseResponse, DateRange
from app.core.services.date_range import date_range

router = APIRouter(prefix="/database", tags=["database"])


@router.post("/profile/reload", deprecated=True)
async def reload_profile():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Данная операция недопустима!",
    )


@router.post(
    "/{table}/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=DatabaseResponse,
    response_model_exclude_none=True,
)
async def load_database(
    table: OfmTableName,
    mode: LoadMode,
    date_range: DateRange,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskDatabase(
        table=table,
        mode=mode,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    response = DatabaseResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.get("/{table}", response_model=dict)
async def get_dates(table: OfmTableName, holder: HolderDep, user: UserDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}
