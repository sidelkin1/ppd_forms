import logging
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from arq import create_pool as create_redis
from arq.connections import ArqRedis, RedisSettings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import close_all_sessions, sessionmaker
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.api.dependencies.dao.provider import DbProvider
from app.core.config.settings import Settings
from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.holder import HolderDAO
from app.initial_data import (
    initialize_all,
    initialize_mapper,
    initialize_replace,
)
from tests.mocks.holder import HolderMock

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def holder(session: AsyncSession) -> HolderDAO:
    return HolderMock(local_session=session)


@pytest_asyncio.fixture(scope="session")
async def pool_holder(pool: sessionmaker) -> HolderDAO:
    return HolderMock(local_pool=pool)


@pytest.fixture(scope="session")
def process_pool(
    settings: Settings,
) -> Generator[ProcessPoolManager, None, None]:
    pool = ProcessPoolManager(settings)
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
    redis_settings: RedisSettings,
) -> AsyncGenerator[ArqRedis, None]:
    redis = await create_redis(redis_settings)
    await redis.flushall()
    yield redis
    await redis.close()


@pytest.fixture(scope="session")
def redis_settings() -> Generator[RedisSettings, None, None]:
    redis_container = RedisContainer("redis:latest")
    if (
        os.name == "nt"
    ):  # TODO workaround from testcontainers/testcontainers-python#108
        redis_container.get_container_host_ip = lambda: "localhost"
    try:
        redis_container.start()
        url = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(redis_container.port_to_expose)
        settings = RedisSettings(host=url, port=int(port))
        yield settings
    finally:
        redis_container.stop()


@pytest.fixture(scope="session")
def settings(
    postgres_url: str, redis_settings: RedisSettings, data_dir: Path
) -> Settings:
    return Settings(
        local_database_url=postgres_url,
        redis_settings=redis_settings,
        well_profile_path=data_dir / "well_profile.csv",
        monthly_report_path=data_dir / "monthly_report.csv",
        inj_well_database_path=data_dir / "inj_well_database.csv",
        neighborhood_path=data_dir / "neighborhood.csv",
        new_strategy_inj_path=data_dir / "new_strategy_inj.csv",
        new_strategy_oil_path=data_dir / "new_strategy_oil.csv",
    )


@pytest.fixture(scope="session")
def alembic_config(settings: Settings) -> AlembicConfig:
    alembic_cfg = AlembicConfig(str(settings.base_dir / "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location",
        str(
            settings.base_dir / "app" / "infrastructure" / "db" / "migrations"
        ),
    )
    alembic_cfg.set_main_option(
        "sqlalchemy.url", str(settings.local_database_url)
    )
    return alembic_cfg


@pytest.fixture(scope="session", autouse=True)
def upgrade_schema_db(alembic_config: AlembicConfig) -> None:
    upgrade(alembic_config, "head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db(
    upgrade_schema_db, pool: sessionmaker, settings: Settings
) -> None:
    provider = DbProvider(local_pool=pool)
    await initialize_replace(provider, settings)
    await initialize_mapper(provider)
    await initialize_all(provider, settings)
