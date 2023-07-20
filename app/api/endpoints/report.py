from pathlib import Path
from typing import Optional

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException,
                     Response, status)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.local_db import get_async_session
from app.api.dependencies.file_lock import current_result_path, get_result_path
from app.schemas.database import DateRange
from app.services.profile_report import create_report

router = APIRouter()


@router.post('/data', status_code=status.HTTP_201_CREATED)
async def generate_report(
    update: DateRange,
    background_tasks: BackgroundTasks,
    path: Path = Depends(get_result_path),
    session: AsyncSession = Depends(get_async_session),
):
    background_tasks.add_task(
        create_report,
        path,
        update.date_from,
        update.date_to,
        session,
    )
    return {'id': path.stem}


@router.get('/data/{file_id}')
async def get_report(
    response: Response,
    path: Optional[Path] = Depends(current_result_path),
):
    if path is None:
        response.status_code = status.HTTP_202_ACCEPTED
        return {'message': 'Отчет не готов!'}
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Файл не найден!',
        )
    return FileResponse(path, media_type='text/csv')
