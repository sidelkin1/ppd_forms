from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.path import PathDep
from app.api.dependencies.redis import RedisDep
from app.api.utils.validators import check_file_exists
from app.core.models.dto import TaskMatrix, TaskOilLoss, TaskReport
from app.core.models.enums import LossMode, ReportName
from app.core.models.schemas import (
    DateRange,
    MatrixEffect,
    MatrixResponse,
    OilLossResponse,
    ReportResponse,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/oil_loss/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=OilLossResponse,
    response_model_exclude_none=True,
)
async def generate_oil_loss_report(
    mode: LossMode,
    date_range: DateRange,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskOilLoss(
        name=ReportName.oil_loss,
        mode=mode,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    response = OilLossResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.post(
    "/matrix",
    status_code=status.HTTP_201_CREATED,
    response_model=MatrixResponse,
    response_model_exclude_none=True,
)
async def generate_matrix_report(
    matrix_effect: MatrixEffect,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskMatrix(
        name=ReportName.matrix,
        date_from=matrix_effect.date_from,
        date_to=matrix_effect.date_to,
        base_period=matrix_effect.base_period,
        pred_period=matrix_effect.pred_period,
        excludes=matrix_effect.excludes,
        on_date=matrix_effect.on_date,
    )
    response = MatrixResponse(task=task, job=job)
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
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskReport(
        name=name,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    response = ReportResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.get("/{file_id}")
async def download_report(file_id: str, user: UserDep, path: PathDep):
    file_path = path.file_path(user.username, file_id)
    check_file_exists(file_path)
    return FileResponse(file_path, media_type="text/csv")


@router.delete("/{file_id}", response_model=dict)
async def delete_report(file_id: str, user: UserDep, path: PathDep):
    file_path = path.file_path(user.username, file_id)
    check_file_exists(file_path)
    file_path.unlink(missing_ok=True)
    return {"message": "Отчет удален!"}
