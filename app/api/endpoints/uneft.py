from fastapi import APIRouter

from app.api.dependencies.redis import RedisDep
from app.api.dependencies.responses import (
    FieldsResponseDep,
    ReservoirsResponseDep,
)
from app.api.utils.validators import check_field_exists
from app.core.models.dto import UneftFieldDB, UneftReservoirDB

router = APIRouter()


@router.get("/fields", response_model=list[UneftFieldDB])
async def field_list(response: FieldsResponseDep, redis: RedisDep):
    fields = await redis.result(response)
    return fields


@router.get(
    "/fields/{field_id}/reservoirs", response_model=list[UneftReservoirDB]
)
async def reservoir_list(
    field_id: int,
    fields_response: FieldsResponseDep,
    reservoirs_response: ReservoirsResponseDep,
    redis: RedisDep,
):
    fields = await redis.result(fields_response)
    check_field_exists(field_id, fields)
    reservoirs = await redis.result(reservoirs_response)
    return reservoirs
