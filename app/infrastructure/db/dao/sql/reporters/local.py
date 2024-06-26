import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.dao.sql.reporters.base import BaseDAO


class LocalBaseDAO(BaseDAO[async_sessionmaker[AsyncSession]]):
    async def _perform_query(
        self, queryset: Select | CompoundSelect, **params
    ) -> pd.DataFrame:
        def pandas_query(session: Session) -> pd.DataFrame:
            return pd.read_sql_query(
                queryset, session.connection(), params=params
            )

        async with self.pool() as session:
            result = await session.run_sync(pandas_query)
        return result
