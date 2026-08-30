from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def session_provider() -> AsyncSession:
    raise NotImplementedError


class SessionProvider:
    """Единственная обязанность: выдать AsyncSession из пула."""

    def __init__(self, pool: async_sessionmaker[AsyncSession]) -> None:
        self.pool = pool

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.pool() as session:
            yield session


DbSessionDep = Annotated[AsyncSession, Depends(session_provider)]
