"""Sessions: владение пулами и выдача сессий/соединений (SRP)."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass

from arq import ArqRedis
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.db.config.models.ofm import OracleSettings
from app.infrastructure.db.factories.local import (
    create_engine as create_local_engine,
)
from app.infrastructure.db.factories.local import (
    create_session_maker as create_local_session_maker,
)
from app.infrastructure.db.factories.ofm import (
    create_engine as create_ofm_engine,
)
from app.infrastructure.db.factories.ofm import (
    create_session_maker as create_ofm_session_maker,
)
from app.infrastructure.exceptions import (
    OfmPoolNotConfiguredError,
    RedisPoolNotConfiguredError,
)
from app.infrastructure.redis.config.models.redis import RedisSettings
from app.infrastructure.redis.factory import (
    create_pool as create_redis_maker,
)
from app.infrastructure.redis.factory import redismaker


@dataclass(frozen=True)
class Sessions:
    local: async_sessionmaker[AsyncSession]
    local_engine: AsyncEngine
    ofm: sessionmaker[Session] | None = None
    ofm_engine: Engine | None = None
    redis: redismaker[ArqRedis] | None = None

    @classmethod
    def create(
        cls,
        local_settings: PostgresSettings,
        ofm_settings: OracleSettings | None = None,
        redis_settings: RedisSettings | None = None,
    ) -> Sessions:
        """Собирает пулы из настроек (production-пути).

        Тесты используют явный конструктор: им нужны кастомные engine
        (NullPool) и sessionmaker (expire_on_commit=False).
        OFM-настройки передаются только если рефлексия моделей прошла
        успешно (проверка `ofm.setup` — снаружи, не здесь).
        """
        local_engine = create_local_engine(local_settings)
        ofm_engine = create_ofm_engine(ofm_settings) if ofm_settings else None
        return cls(
            local=create_local_session_maker(local_engine),
            local_engine=local_engine,
            ofm=create_ofm_session_maker(ofm_engine) if ofm_engine else None,
            ofm_engine=ofm_engine,
            redis=(
                create_redis_maker(redis_settings) if redis_settings else None
            ),
        )

    @asynccontextmanager
    async def local_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.local() as session:
            yield session

    @contextmanager
    def ofm_session(self) -> Generator[Session, None, None]:
        if self.ofm is None:
            raise OfmPoolNotConfiguredError(
                "OFM (Oracle) пул не сконфигурирован"
            )
        with self.ofm() as session:
            yield session

    @asynccontextmanager
    async def redis_conn(self) -> AsyncGenerator[ArqRedis, None]:
        if self.redis is None:
            raise RedisPoolNotConfiguredError("Redis пул не сконфигурирован")
        async with self.redis() as client:
            yield client

    async def dispose(self) -> None:
        await self.local_engine.dispose()
        if self.ofm_engine is not None:
            self.ofm_engine.dispose()
