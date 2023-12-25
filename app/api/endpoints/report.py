from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.responses import (
    OilLossResponseDep,
    ReportResponseDep,
)
from app.api.dependencies.user import UserFileDep
from app.api.utils.validators import check_file_exists
from app.core.models.enums import LossMode, ReportName
from app.core.models.schemas import DateRange, OilLossResponse, ReportResponse

router = APIRouter()


@router.post(
    "/oil_loss/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=OilLossResponse,
    response_model_exclude_none=True,
)
async def generate_oil_loss_report(
    mode: LossMode,
    date_range: DateRange,
    response: OilLossResponseDep,
    redis: RedisDep,
):
    await redis.enqueue_task(response)
    return response


@router.post(
    "/{name}",
    status_code=status.HTTP_201_CREATED,
    response_model=ReportResponse,
    response_model_exclude_none=True,
)
async def generate_report(
    name: ReportName,
    date_range: DateRange,
    response: ReportResponseDep,
    redis: RedisDep,
):
    await redis.enqueue_task(response)
    return response


@router.get("/{file_id}")
async def download_report(file_id: str, path: UserFileDep):
    check_file_exists(path)
    return FileResponse(path, media_type="text/csv")


@router.delete("/{file_id}", response_model=dict)
async def delete_report(file_id: str, path: UserFileDep):
    check_file_exists(path)
    path.unlink(missing_ok=True)
    return {"message": "Отчет удален!"}
