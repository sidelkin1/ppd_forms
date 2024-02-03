from fastapi import APIRouter, UploadFile, status

from app.api.dependencies.auth import UserDep
from app.api.dependencies.db import HolderDep
from app.api.dependencies.path import PathDep
from app.api.dependencies.redis import RedisDep
from app.api.utils.upload_file import save_upload_file
from app.core.models.dto import JobStamp, TaskExcel
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath, ExcelResponse
from app.core.services.date_range import date_range

router = APIRouter()


@router.post("/", response_model=dict)
async def upload_file(file: UploadFile, user: UserDep, path: PathDep):
    await save_upload_file(file, path.upload_dir(user.username))
    return {"filename": file.filename}


@router.post(
    "/{table}/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=ExcelResponse,
    response_model_exclude_none=True,
)
async def load_database(
    table: ExcelTableName,
    mode: LoadMode,
    excel: ExcelPath,
    user: UserDep,
    redis: RedisDep,
):
    task = TaskExcel(table=table, mode=mode, file=excel.file)
    response = ExcelResponse(task=task, job=JobStamp(user_id=user.username))
    await redis.enqueue_task(response)
    return response


@router.get("/{table}", response_model=dict)
async def get_dates(table: ExcelTableName, holder: HolderDep, user: UserDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}
