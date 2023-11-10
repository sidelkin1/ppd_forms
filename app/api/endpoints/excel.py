import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status

from app.api.dependencies.dao.provider import HolderDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.tasks import TaskExcelDep
from app.api.dependencies.user import UserDirDep
from app.api.endpoints.websocket import websocket_endpoint
from app.core.config.settings import settings
from app.core.models.dto import TaskExcel
from app.core.models.enums import ExcelTableName, LoadMode
from app.core.models.schemas import ExcelPath, TaskResponse
from app.core.services.date_range import date_range

router = APIRouter()

COPY_BUFSIZE = 1024 * 1024


@router.post("/")
async def upload_file(file: UploadFile):
    path = settings.base_dir / "excel" / file.filename
    try:
        async with aiofiles.open(path, "wb") as f:
            while contents := await file.read(COPY_BUFSIZE):
                await f.write(contents)
    except Exception:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при загрузке файла!",
        )  # TODO log
    finally:
        await file.close()
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
    return TaskResponse[TaskExcel](task=task, job=job_stamp)


@router.get("/{table}")
async def get_dates(table: ExcelTableName, holder: HolderDep):
    min_date, max_date = await date_range(table, holder)
    return {"min_date": min_date, "max_date": max_date}


router.add_api_websocket_route("/ws", websocket_endpoint)
