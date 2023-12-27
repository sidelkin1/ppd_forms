import asyncio
from typing import Generic, TypeVar

import pandas as pd
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import Select

Pool = TypeVar(
    "Pool",
    bound=sessionmaker[Session] | async_sessionmaker[AsyncSession],
    covariant=True,
    contravariant=False,
)


class BaseDAO(Generic[Pool]):
    def __init__(self, querysets: dict[str, Select], pool: Pool) -> None:
        self.querysets = list(querysets.values())
        self.keys = list(querysets.keys())
        self.pool = pool

    async def _perform_query(self, queryset: Select, **params) -> Result:
        raise NotImplementedError

    async def read_one(
        self, *, key: str | None = None, **params
    ) -> pd.DataFrame:
        queryset = self.querysets[self.keys.index(key) if key else 0]
        result = await self._perform_query(queryset, **params)
        return pd.DataFrame(result.all())

    async def read_all(self, **params) -> dict[str, pd.DataFrame]:
        results: list[pd.DataFrame] = await asyncio.gather(
            *(self.read_one(key=key, **params) for key in self.keys)
        )
        return dict(zip(self.keys, results))
