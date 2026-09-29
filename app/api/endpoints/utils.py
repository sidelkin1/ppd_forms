from fastapi import APIRouter, UploadFile, status

from app.api.dependencies.auth import UserDep
from app.api.dependencies.job import NewJobDep
from app.api.dependencies.path import PathDep
from app.api.dependencies.redis import RedisDep
from app.api.utils.upload_file import save_upload_file
from app.core.models.dto import TaskUtils, UtilsResponse
from app.core.models.enums import LoadMode, UtilsTableName
from app.core.models.schemas import CsvPath

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post("/", response_model=dict)
async def upload_file(file: UploadFile, user: UserDep, path: PathDep):
    await save_upload_file(file, path.upload_dir(user.username))
    return {"filename": file.filename}


@router.post(
    "/{table}/{mode}",
    status_code=status.HTTP_201_CREATED,
    response_model=UtilsResponse,
    response_model_exclude_none=True,
)
async def load_utils(
    table: UtilsTableName,
    mode: LoadMode,
    csv: CsvPath,
    user: UserDep,
    redis: RedisDep,
    job: NewJobDep,
):
    task = TaskUtils(table=table, mode=mode, file=csv.file)
    response = UtilsResponse(task=task, job=job)
    await redis.enqueue_task(response, user.username)
    return response
