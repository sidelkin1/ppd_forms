from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.api.dependencies.job import NewJobDep
from app.api.dependencies.redis.provider import RedisDep
from app.api.dependencies.tasks import TaskReportDep
from app.api.dependencies.user import FilePathDep, UserDirDep
from app.api.endpoints.websocket import websocket_endpoint
from app.api.validators.validators import check_file_exists
from app.core.models.dto import TaskReport
from app.core.models.enums import ReportName
from app.core.models.schemas import DateRange, TaskResponse

router = APIRouter()


@router.post(
    "/{name}",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskResponse[TaskReport],
    response_model_exclude_none=True,
)
async def generate_report(
    name: ReportName,
    date_range: DateRange,
    task: TaskReportDep,
    redis: RedisDep,
    job_stamp: NewJobDep,
    directory: UserDirDep,
):
    await redis.enqueue_task(task, job_stamp)
    return TaskResponse(task=task, job=job_stamp)


@router.get("/{file_id}")
async def download_report(file_id: str, path: FilePathDep):
    check_file_exists(path)
    return FileResponse(path, media_type="text/csv")


@router.delete("/{file_id}")
async def delete_report(file_id: str, path: FilePathDep):
    check_file_exists(path)
    path.unlink(missing_ok=True)
    return {"message": "Отчет удален!"}


router.add_api_websocket_route("/ws", websocket_endpoint)
