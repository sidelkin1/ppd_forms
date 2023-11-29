from fastapi import APIRouter, UploadFile, status

from app.api.dependencies.dao.provider import HolderDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.tasks import TaskExcelDep
from app.api.dependencies.user import UserDirDep
from app.api.utils.upload_file import save_upload_file
from app.core.models.dto import TaskExcel
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath, TaskResponse
from app.core.services.date_range import date_range

router = APIRouter()


@router.post("/", response_model=dict)
async def upload_file(file: UploadFile):
    await save_upload_file(file)
    return {"filename": file.filename}


@router.post(
    "/{table}/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse[TaskExcel],
    response_model_exclude_none=True,
)
async def load_database(
    table: ExcelTableName,
    mode: LoadMode,
    path: ExcelPath,
    task: TaskExcelDep,
    redis: RedisDep,
    job_stamp: NewJobDep,
    directory: UserDirDep,
):
    await redis.enqueue_task(task, job_stamp)
    return TaskResponse(task=task, job=job_stamp)


@router.get("/{table}", response_model=dict)
async def get_dates(table: ExcelTableName, holder: HolderDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}
