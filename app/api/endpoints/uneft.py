from fastapi import APIRouter

from app.api.dependencies.auth import UserDep
from app.api.dependencies.redis import RedisDep
from app.api.utils.validators import check_field_exists
from app.core.models.dto import (
    JobStamp,
    TaskFields,
    TaskReservoirs,
    UneftFieldDB,
    UneftReservoirDB,
)
from app.core.models.enums import UneftAssets
from app.core.models.schemas import FieldsResponse, ReservoirsResponse
from app.infrastructure.redis.dao import RedisDAO

router = APIRouter()


async def get_fields(
    job_stamp: JobStamp, redis: RedisDAO
) -> list[UneftFieldDB]:
    task = TaskFields(assets=UneftAssets.fields)
    response = FieldsResponse(task=task, job=job_stamp)
    fields = await redis.result(response)
    return fields


@router.get("/fields", response_model=list[UneftFieldDB])
async def field_list(user: UserDep, redis: RedisDep):
    fields = await get_fields(JobStamp(user_id=user.username), redis)
    return fields


@router.get(
    "/fields/{field_id}/reservoirs", response_model=list[UneftReservoirDB]
)
async def reservoir_list(field_id: int, user: UserDep, redis: RedisDep):
    fields = await get_fields(JobStamp(user_id=user.username), redis)
    check_field_exists(field_id, fields)
    task = TaskReservoirs(assets=UneftAssets.reservoirs, field_id=field_id)
    response = ReservoirsResponse(
        task=task, job=JobStamp(user_id=user.username)
    )
    reservoirs = await redis.result(response)
    return reservoirs
