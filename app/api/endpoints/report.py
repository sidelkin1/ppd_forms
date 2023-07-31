from pathlib import Path

from fastapi import (APIRouter, BackgroundTasks, Depends, Request, Response,
                     status)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.file_lock import (file_path_from_id, get_result_path,
                                            result_is_locked)
from app.api.validators import check_file_exists
from app.core.local_db import get_async_session
from app.schemas.database import DateRange
from app.services.profile_report import create_report

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def generate_report(
    update: DateRange,
    background_tasks: BackgroundTasks,
    request: Request,
    path: Path = Depends(get_result_path),
    session: AsyncSession = Depends(get_async_session),
):
    background_tasks.add_task(
        create_report,
        path,
        update.date_from,
        update.date_to,
        session,
        request.app.state.pool_executor,
    )
    return {'file_id': path.stem}


@router.get('/{file_id}/status')
async def get_report_status(
    response: Response,
    not_ready: bool = Depends(result_is_locked),
):
    if not_ready:
        response.status_code = status.HTTP_202_ACCEPTED
        return {'message': 'Отчет не готов!'}
    return {'message': 'Отчет готов!'}


@router.get('/{file_id}')
async def download_report(
    path: Path = Depends(file_path_from_id),
):
    check_file_exists(path)
    return FileResponse(path, media_type='text/csv')


@router.delete('/{file_id}')
async def delete_report(
    path: Path = Depends(file_path_from_id),
):
    check_file_exists(path)
    path.unlink(missing_ok=True)
    return {'message': 'Отчет удален!'}
