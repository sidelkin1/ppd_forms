from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.holder import HolderDAO


def dao_provider() -> HolderDAO:
    raise NotImplementedError


class DbProvider:
    def __init__(
        self,
        *,
        local_pool: async_sessionmaker[AsyncSession] | None = None,
        ofm_pool: sessionmaker[Session] | None = None,
    ) -> None:
        self.local_pool = local_pool
        self.ofm_pool = ofm_pool

    async def local_dao(self) -> AsyncGenerator[HolderDAO, None]:
        async with self.local_pool() as session:
            yield HolderDAO(local_session=session, local_pool=self.local_pool)

    async def ofm_dao(self) -> AsyncGenerator[HolderDAO, None]:
        with self.ofm_pool() as session:
            yield HolderDAO(ofm_session=session, ofm_pool=self.ofm_pool)

    async def ofm_local_dao(self) -> AsyncGenerator[HolderDAO, None]:
        with self.ofm_pool() as ofm_session:
            async with self.local_pool() as local_session:
                yield HolderDAO(
                    local_session=local_session, ofm_session=ofm_session
                )

    async def file_local_dao(
        self, file_path: Path
    ) -> AsyncGenerator[HolderDAO, None]:
        async with self.local_pool() as session:
            yield HolderDAO(local_session=session, file_path=file_path)

    async def dispose(self) -> None:
        if self.local_pool and (engine := self.local_pool.kw.get("bind")):
            engine = cast(AsyncEngine, engine)
            await engine.dispose()
        if self.ofm_pool and (engine := self.ofm_pool.kw.get("bind")):
            engine = cast(Engine, engine)
            engine.dispose()


HolderDep = Annotated[HolderDAO, Depends(dao_provider)]
