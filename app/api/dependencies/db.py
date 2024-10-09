from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.holder import HolderDAO


def dao_provider() -> HolderDAO:
    raise NotImplementedError


class DbProvider:
    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        self.pool = pool

    async def dao(self) -> AsyncGenerator[HolderDAO, None]:
        async with self.pool() as session:
            yield HolderDAO(local_session=session)


HolderDep = Annotated[HolderDAO, Depends(dao_provider)]
