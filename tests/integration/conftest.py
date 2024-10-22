import logging
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from arq import create_pool as create_redis
from arq.connections import ArqRedis
from arq.connections import RedisSettings as ArqRedisSettings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import close_all_sessions, sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.common.config.models.paths import Paths
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.holder import HolderDAO
from app.infrastructure.provider import DbProvider
from app.infrastructure.redis.config.main import RedisSettings
from app.initial_data import (
    initialize_all,
    initialize_mapper,
    initialize_replace,
)
from tests.mocks.holder import HolderMock

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def holder(session: AsyncSession) -> HolderDAO:
    return HolderMock(
        local_session=session, file_path=None, ofm_session=None, ofm_pool=None
    )


@pytest_asyncio.fixture(scope="session")
async def pool_holder(pool: sessionmaker) -> HolderDAO:
    return HolderMock(
        local_pool=pool, file_path=None, ofm_session=None, ofm_pool=None
    )


@pytest.fixture(scope="session")
def process_pool() -> Generator[ProcessPoolManager, None, None]:
    pool = ProcessPoolManager(max_workers=1)
    yield pool
    pool.close()


@pytest_asyncio.fixture
async def session(pool: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with pool() as session_:
        yield session_


@pytest.fixture(scope="session")
def pool(postgres_url: str) -> Generator[sessionmaker, None, None]:
    engine = create_async_engine(
        url=postgres_url,
        poolclass=NullPool,  # FIXME workaround for pytest-asyncio==0.23.3
    )
    pool_: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False
    )
    yield pool_  # type: ignore[misc]
    close_all_sessions()


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    postgres = PostgresContainer("postgres:latest")
    if (
        os.name == "nt"
    ):  # TODO workaround from testcontainers/testcontainers-python#108
        postgres.get_container_host_ip = lambda: "localhost"
    try:
        postgres.start()
        postgres_url_ = postgres.get_connection_url().replace(
            "psycopg2", "asyncpg"
        )
        logger.info("postgres url %s", postgres_url_)
        yield postgres_url_
    finally:
        postgres.stop()


@pytest_asyncio.fixture
async def arq_redis(
    arq_settings: ArqRedisSettings,
) -> AsyncGenerator[ArqRedis, None]:
    redis = await create_redis(arq_settings)
    await redis.flushall()
    yield redis
    await redis.close()


@pytest.fixture(scope="session")
def arq_settings() -> Generator[ArqRedisSettings, None, None]:
    redis_container = RedisContainer("redis:latest")
    if (
        os.name == "nt"
    ):  # TODO workaround from testcontainers/testcontainers-python#108
        redis_container.get_container_host_ip = lambda: "localhost"
    try:
        redis_container.start()
        url = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(redis_container.port_to_expose)
        settings = ArqRedisSettings(host=url, port=int(port))
        yield settings
    finally:
        redis_container.stop()


@pytest.fixture(scope="session")
def postgres_config(postgres_url: str) -> PostgresSettings:
    return PostgresSettings(  # type: ignore[call-arg]
        local_database_url=postgres_url
    )


@pytest.fixture(scope="session")
def redis_config(arq_settings: ArqRedisSettings) -> RedisSettings:
    return RedisSettings(arq_settings=arq_settings)


@pytest.fixture(scope="session")
def alembic_config(paths: Paths, postgres_url: str) -> AlembicConfig:
    alembic_cfg = AlembicConfig(str(paths.base_dir / "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location",
        str(paths.base_dir / "app" / "infrastructure" / "db" / "migrations"),
    )
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_url)
    return alembic_cfg


@pytest.fixture(scope="session", autouse=True)
def upgrade_schema_db(alembic_config: AlembicConfig) -> None:
    upgrade(alembic_config, "head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db(
    upgrade_schema_db, pool: sessionmaker, paths: Paths
) -> None:
    provider = DbProvider(local_pool=pool)
    await initialize_replace(provider, paths)
    await initialize_mapper(provider)
    await initialize_all(provider, paths)
