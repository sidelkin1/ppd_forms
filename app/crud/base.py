from datetime import date

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Select

from app.core.local_db import Base


class CRUDBase:

    def __init__(self, model: type[Base]):
        self.model = model

    async def get_ofm_data(self, stmt: Select, session: Session) -> list[Row]:
        result = await run_in_threadpool(session.execute, stmt)
        return result.all()

    async def get_min_max_dates(
        self,
        session: AsyncSession,
    ) -> tuple[date, date]:
        result = await session.execute(
            select(
                func.min(self.model.date_stamp),
                func.max(self.model.date_stamp),
            )
        )
        return result.one()
