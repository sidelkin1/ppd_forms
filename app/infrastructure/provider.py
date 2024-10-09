from collections.abc import AsyncGenerator
from typing import cast

from arq import ArqRedis
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.holder import HolderDAO
from app.infrastructure.redis.factory import redismaker


class DbProvider:
    def __init__(
        self,
        *,
        local_pool: async_sessionmaker[AsyncSession] | None = None,
        ofm_pool: sessionmaker[Session] | None = None,
        redis_pool: redismaker[ArqRedis] | None = None,
    ) -> None:
        self.local_pool = local_pool
        self.ofm_pool = ofm_pool
        self.redis_pool = redis_pool

    async def local_dao(self, **kwargs) -> AsyncGenerator[HolderDAO, None]:
        async with self.local_pool() as session:
            yield HolderDAO(
                local_session=session, local_pool=self.local_pool, **kwargs
            )

    async def ofm_dao(self, **kwargs) -> AsyncGenerator[HolderDAO, None]:
        with self.ofm_pool() as session:
            yield HolderDAO(
                ofm_session=session, ofm_pool=self.ofm_pool, **kwargs
            )

    async def ofm_local_dao(self, **kwargs) -> AsyncGenerator[HolderDAO, None]:
        with self.ofm_pool() as ofm_session:
            async with self.local_pool() as local_session:
                yield HolderDAO(
                    local_session=local_session,
                    ofm_session=ofm_session,
                    local_pool=self.local_pool,
                    ofm_pool=self.ofm_pool,
                    **kwargs,
                )

    async def ofm_redis_dao(self, **kwargs) -> AsyncGenerator[HolderDAO, None]:
        with self.ofm_pool() as ofm_session:
            async with self.redis_pool() as redis:
                yield HolderDAO(
                    redis=redis,
                    ofm_session=ofm_session,
                    ofm_pool=self.ofm_pool,
                    **kwargs,
                )

    async def dispose(self) -> None:
        if self.local_pool and (engine := self.local_pool.kw.get("bind")):
            engine = cast(AsyncEngine, engine)
            await engine.dispose()
        if self.ofm_pool and (engine := self.ofm_pool.kw.get("bind")):
            engine = cast(Engine, engine)
            engine.dispose()
