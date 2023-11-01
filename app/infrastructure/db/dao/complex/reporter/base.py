import asyncio

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql.expression import Select


class BaseDAO:
    def __init__(
        self,
        querysets: dict[str, Select],
        pool: async_sessionmaker[AsyncSession],
    ) -> None:
        self.querysets = list(querysets.values())
        self.keys = list(querysets.keys())
        self.pool = pool

    async def read_one(
        self, *, key: str | None = None, **params
    ) -> pd.DataFrame:
        queryset = self.querysets[self.keys.index(key) if key else 0]
        async with self.pool() as session:
            result = await session.execute(queryset, params)
        return pd.DataFrame(result.all())

    async def read_all(self, **params) -> dict[str, pd.DataFrame]:
        results: list[pd.DataFrame] = await asyncio.gather(
            *(self.read_one(key=key, **params) for key in self.keys)
        )
        return dict(zip(self.keys, results))
