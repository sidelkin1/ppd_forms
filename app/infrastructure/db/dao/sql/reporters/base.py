import asyncio
from typing import Generic, TypeVar

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql.expression import CompoundSelect, Select

Pool = TypeVar(
    "Pool",
    bound=sessionmaker[Session] | async_sessionmaker[AsyncSession],
    covariant=True,
    contravariant=False,
)


class BaseDAO(Generic[Pool]):
    def __init__(
        self, querysets: dict[str, Select | CompoundSelect], pool: Pool
    ) -> None:
        self.querysets = list(querysets.values())
        self.keys = list(querysets.keys())
        self.pool = pool

    async def _perform_query(
        self, queryset: Select | CompoundSelect, **params
    ) -> pd.DataFrame:
        raise NotImplementedError

    async def read_one(
        self, *, key: str | None = None, **params
    ) -> pd.DataFrame:
        queryset = self.querysets[self.keys.index(key) if key else 0]
        df = await self._perform_query(queryset, **params)
        return df

    async def read_all(self, **params) -> dict[str, pd.DataFrame]:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(self.read_one(key=key, **params))
                for key in self.keys
            ]
        return dict(zip(self.keys, (task.result() for task in tasks)))
