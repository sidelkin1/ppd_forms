from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.path import PathDep
from app.api.dependencies.redis import RedisDep
from app.api.models.responses import (
    FnvResponse,
    InjLossResponse,
    MatbalResponse,
    MatrixResponse,
    MmbResponse,
    OilLossResponse,
    ProlongResponse,
    ReportResponse,
)
from app.api.utils.validators import check_file_exists
from app.core.models.dto import (
    TaskFNV,
    TaskInjLoss,
    TaskMatbal,
    TaskMatrix,
    TaskMmb,
    TaskOilLoss,
    TaskProlong,
    TaskReport,
)
from app.core.models.enums import FileExtension, LossMode, ReportName
from app.core.models.schemas import (
    DateRange,
    FnvParams,
    MatbalParams,
    MatrixEffect,
    MmbParams,
    ProlongParams,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/inj_loss/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=InjLossResponse,
    response_model_exclude_none=True,
)
async def generate_inj_loss_report(
    mode: LossMode,
    date_range: DateRange,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskInjLoss(
        name=ReportName.inj_loss,
        mode=mode,
        date_from=date_range.date_from,
        date_to=date_range.date_to,
    )
    response = InjLossResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.post(
    "/oil_loss/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=InjLossResponse,
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
    "/fnv",
    status_code=status.HTTP_201_CREATED,
    response_model=FnvResponse,
    response_model_exclude_none=True,
)
async def generate_fnv_report(
    params: FnvParams,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskFNV(
        name=ReportName.fnv,
        fields=params.fields,
        min_radius=params.min_radius,
        alternative=params.alternative,
    )
    response = FnvResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.post(
    "/matbal",
    status_code=status.HTTP_201_CREATED,
    response_model=MatbalResponse,
    response_model_exclude_none=True,
)
async def generate_matbal_report(
    params: MatbalParams,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskMatbal(
        name=ReportName.matbal,
        field=params.field,
        reservoirs=params.reservoirs,
        wells=params.wells,
        measurements=params.measurements,
        alternative=params.alternative,
    )
    response = MatbalResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.post(
    "/prolong",
    status_code=status.HTTP_201_CREATED,
    response_model=ProlongResponse,
    response_model_exclude_none=True,
)
async def generate_prolong_report(
    params: ProlongParams,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskProlong(
        name=ReportName.prolong,
        expected=params.expected,
        actual=params.actual,
        interpolation=params.interpolation,
    )
    response = ProlongResponse(task=task, job=job)
    await redis.enqueue_task(response)
    return response


@router.post(
    "/mmb",
    status_code=status.HTTP_201_CREATED,
    response_model=MmbResponse,
    response_model_exclude_none=True,
)
async def generate_mmb_report(
    params: MmbParams,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskMmb(
        name=ReportName.matbal,
        file=params.file,
        alternative=params.alternative,
    )
    response = MmbResponse(task=task, job=job)
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


@router.get("/{file_id}/{ext}")
async def download_report(
    file_id: str, ext: FileExtension, user: UserDep, path: PathDep
):
    file_path = path.file_path(user.username, file_id, ext=ext.value)
    check_file_exists(file_path)
    return FileResponse(file_path, filename=file_path.name)


@router.delete("/{file_id}/{ext}", response_model=dict)
async def delete_report(
    file_id: str, ext: FileExtension, user: UserDep, path: PathDep
):
    file_path = path.file_path(user.username, file_id, ext=ext.value)
    check_file_exists(file_path)
    file_path.unlink(missing_ok=True)
    return {"message": "Отчет удален!"}
