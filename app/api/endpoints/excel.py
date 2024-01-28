from fastapi import APIRouter, UploadFile, status

from app.api.dependencies.db import HolderDep
from app.api.dependencies.redis import RedisDep
from app.api.dependencies.responses import ExcelResponseDep
from app.api.dependencies.user import UserDirDep
from app.api.utils.upload_file import save_upload_file
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath, ExcelResponse
from app.core.services.date_range import date_range

router = APIRouter()


@router.post("/", response_model=dict)
async def upload_file(file: UploadFile, user_dir: UserDirDep):
    await save_upload_file(file, user_dir / "uploads")
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
    path: ExcelPath,
    response: ExcelResponseDep,
    redis: RedisDep,
):
    await redis.enqueue_task(response)
    return response


@router.get("/{table}", response_model=dict)
async def get_dates(table: ExcelTableName, holder: HolderDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}
