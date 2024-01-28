from fastapi import APIRouter, HTTPException, status

from app.api.dependencies.db import HolderDep
from app.api.dependencies.redis import RedisDep
from app.api.dependencies.responses import DatabaseResponseDep
from app.core.models.enums import LoadMode, OfmTableName
from app.core.models.schemas import DatabaseResponse, DateRange
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
    response_model=DatabaseResponse,
    response_model_exclude_none=True,
)
async def load_database(
    table: OfmTableName,
    mode: LoadMode,
    date_range: DateRange,
    response: DatabaseResponseDep,
    redis: RedisDep,
):
    await redis.enqueue_task(response)
    return response


@router.get("/{table}", response_model=dict)
async def get_dates(table: OfmTableName, holder: HolderDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}
