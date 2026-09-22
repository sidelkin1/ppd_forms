import logging

from fastapi import APIRouter

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import NewJobDep, create_job_stamp
from app.api.dependencies.redis import RedisDep
from app.api.utils.validators import check_field_exists
from app.core.models.dto import (
    FieldsResponse,
    ReservoirsResponse,
    TaskFields,
    TaskReservoirs,
    TaskWells,
    UneftFieldDB,
    UneftReservoirDB,
    UneftWellDB,
    WellsResponse,
)
from app.core.models.enums import UneftAssets, WellStock

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uneft", tags=["uneft"])


@router.get("/fields", response_model=list[UneftFieldDB])
async def field_list(
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
    stock: WellStock = WellStock.all,
):
    task = TaskFields(assets=UneftAssets.fields, stock=stock)
    response = FieldsResponse(task=task, job=job)
    await redis.enqueue_task(response, user.username)
    fields: list[UneftFieldDB] = await redis.result(
        response.job.job_id, user.username
    )
    logger.debug("Fetched fields", extra={"fields": fields})
    return fields


@router.get("/fields/{field_id}", response_model=UneftFieldDB)
async def get_field(
    field_id: int,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
    stock: WellStock = WellStock.all,
):
    task = TaskFields(
        assets=UneftAssets.fields, stock=stock, field_id=field_id
    )
    response = FieldsResponse(task=task, job=job)
    await redis.enqueue_task(response, user.username)
    field: UneftFieldDB | None = await redis.result(
        response.job.job_id, user.username
    )
    check_field_exists(field)
    logger.debug("Fetched field", extra={"field": field})
    return field


@router.get(
    "/fields/{field_id}/reservoirs", response_model=list[UneftReservoirDB]
)
async def reservoir_list(field_id: int, user: UserDep, redis: RedisDep):
    await get_field(field_id, user, redis, create_job_stamp(user))
    task = TaskReservoirs(assets=UneftAssets.reservoirs, field_id=field_id)
    response = ReservoirsResponse(task=task, job=create_job_stamp(user))
    await redis.enqueue_task(response, user.username)
    reservoirs: list[UneftReservoirDB] = await redis.result(
        response.job.job_id, user.username
    )
    logger.debug(
        "Fetched reservoirs",
        extra={"field_id": field_id, "reservoirs": reservoirs},
    )
    return reservoirs


@router.get("/fields/{field_id}/wells", response_model=list[UneftWellDB])
async def well_list(
    field_id: int,
    user: UserDep,
    redis: RedisDep,
    stock: WellStock = WellStock.all,
):
    await get_field(field_id, user, redis, create_job_stamp(user))
    task = TaskWells(assets=UneftAssets.wells, stock=stock, field_id=field_id)
    response = WellsResponse(task=task, job=create_job_stamp(user))
    await redis.enqueue_task(response, user.username)
    wells: list[UneftWellDB] = await redis.result(
        response.job.job_id, user.username
    )
    logger.debug(
        "Fetched wells",
        extra={"field_id": field_id, "reservoirs": wells},
    )
    return wells
