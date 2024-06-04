from fastapi.concurrency import run_in_threadpool
from sqlalchemy import Result
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.dao.sql.reporters.base import BaseDAO


class OfmBaseDAO(BaseDAO[sessionmaker[Session]]):
    async def _perform_query(
        self, queryset: Select | CompoundSelect, **params
    ) -> Result:
        with self.pool() as session:
            result = await run_in_threadpool(session.execute, queryset, params)
        return result
