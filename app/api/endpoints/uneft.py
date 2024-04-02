import logging

from fastapi import APIRouter

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import JobDep, NewJobDep
from app.api.dependencies.redis import RedisDep
from app.api.models.responses import FieldsResponse, ReservoirsResponse
from app.api.utils.validators import check_field_exists
from app.core.models.dto import (
    JobStamp,
    TaskFields,
    TaskReservoirs,
    UneftFieldDB,
    UneftReservoirDB,
)
from app.core.models.enums import UneftAssets
from app.infrastructure.redis.dao import RedisDAO

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uneft", tags=["uneft"])


async def get_fields(
    job_stamp: JobStamp, redis: RedisDAO
) -> list[UneftFieldDB]:
    task = TaskFields(assets=UneftAssets.fields)
    response = FieldsResponse(task=task, job=job_stamp)
    fields = await redis.result(response)
    logger.debug("Fetched fields", extra={"fields": fields})
    return fields


@router.get("/fields", response_model=list[UneftFieldDB])
async def field_list(user: UserDep, redis: RedisDep, job: NewJobDep):
    fields = await get_fields(job, redis)
    return fields


@router.get(
    "/fields/{field_id}/reservoirs", response_model=list[UneftReservoirDB]
)
async def reservoir_list(
    field_id: int, user: UserDep, redis: RedisDep, job: JobDep
):
    fields = await get_fields(await job.create(user), redis)
    check_field_exists(field_id, fields)
    task = TaskReservoirs(assets=UneftAssets.reservoirs, field_id=field_id)
    response = ReservoirsResponse(task=task, job=await job.create(user))
    reservoirs = await redis.result(response)
    logger.debug(
        "Fetched reservoirs",
        extra={"field_id": field_id, "reservoirs": reservoirs},
    )
    return reservoirs
