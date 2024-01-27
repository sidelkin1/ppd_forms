from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import CompoundSelect, Select

from app.infrastructure.db.dao.sql.reporters.base import BaseDAO


class LocalBaseDAO(BaseDAO[async_sessionmaker[AsyncSession]]):
    async def _perform_query(
        self, queryset: Select | CompoundSelect, **params
    ) -> Result:
        async with self.pool() as session:
            result = await session.execute(queryset, params)
        return result
