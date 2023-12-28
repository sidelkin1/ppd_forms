from fastapi.concurrency import run_in_threadpool
from sqlalchemy import Result
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.dao.sql.reporters.base import BaseDAO


class OfmBaseDAO(BaseDAO[sessionmaker[Session]]):
    async def _perform_query(self, queryset: Select, **params) -> Result:
        with self.pool() as session:
            result: Result = await run_in_threadpool(
                session.execute, queryset, params
            )
        return result
