import pandas as pd
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.dao.sql.reporters.base import BaseDAO


class OfmBaseDAO(BaseDAO[sessionmaker[Session]]):
    async def _perform_query(
        self, queryset: Select | CompoundSelect, **params
    ) -> pd.DataFrame:
        with self.pool() as session:
            df = await run_in_threadpool(
                pd.read_sql_query,
                queryset,
                session.connection(),
                params=params,
            )
        return df
