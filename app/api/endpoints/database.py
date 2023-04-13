from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.api.mappings import LoadMode, TableName
from app.core.local_db import get_async_session as get_local_session
from app.core.ofm_db import get_session as get_ofm_session
from app.schemas.database import DateRange

router = APIRouter()


@router.post('/profile/reload', deprecated=True)
async def profile_reload():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail='Данная операция недопустима!',
    )


@router.post('/{table}/{mode}', status_code=status.HTTP_201_CREATED)
async def start_database_load(
        table: TableName,
        mode: LoadMode,
        update: DateRange,
        background_tasks: BackgroundTasks,
        local_session: AsyncSession = Depends(get_local_session),
        ofm_session: Session = Depends(get_ofm_session),
):
    background_tasks.add_task(
        mode(table.crud),
        update.date_from,
        update.date_to,
        local_session,
        ofm_session,
    )
    return {'message': 'Запущен процесс выгрузки из БД'}


@router.get('/{table}')
async def get_database_dates(
    table: TableName,
    session: AsyncSession = Depends(get_local_session),
):
    min_date, max_date = await table.crud.get_min_max_dates(session)
    return {'min_date': min_date, 'max_date': max_date}
