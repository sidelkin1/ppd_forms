import logging
import os
from collections.abc import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from arq import create_pool as create_redis
from arq.connections import ArqRedis, RedisSettings
from arq.worker import Worker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import close_all_sessions, sessionmaker
from starlette.middleware.sessions import SessionMiddleware
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.api import dependencies
from app.api.routes.routers import main_router
from app.core.config.settings import Settings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.lifespan import lifespan

logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def session(pool: sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with pool() as session_:
        yield session_


@pytest.fixture(scope="session")
def pool(postgres_url: str) -> Generator[sessionmaker, None, None]:
    engine = create_async_engine(url=postgres_url)
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


@pytest_asyncio.fixture(scope="session")
async def arq_redis(redis_settings: RedisSettings) -> ArqRedis:
    redis = await create_redis(redis_settings)
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


@pytest_asyncio.fixture(scope="session")
async def worker(
    arq_redis: ArqRedis,
) -> Generator[Callable[..., Worker], None, None]:
    worker_: Worker = None

    def create(
        functions=[],
        burst=True,
        poll_delay=0,
        max_jobs=10,
        arq_redis=arq_redis,
        **kwargs,
    ) -> Worker:
        nonlocal worker_
        worker_ = Worker(
            functions=functions,
            redis_pool=arq_redis,
            burst=burst,
            poll_delay=poll_delay,
            max_jobs=max_jobs,
            **kwargs,
        )
        return worker_

    yield create
    if worker_:
        await worker_.close()


@pytest.fixture(scope="session")
def settings(postgres_url: str, redis_settings: RedisSettings) -> Settings:
    return Settings(
        local_database_url=postgres_url, redis_settings=redis_settings
    )


@pytest.fixture(scope="session")
def app(settings: Settings) -> FastAPI:
    pool = create_local_pool(settings)
    redis = create_redis_pool(settings)
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        lifespan=lifespan,
    )
    app.add_middleware(SessionMiddleware, secret_key=os.urandom(32))
    app.include_router(main_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.state.settings = settings  # needed for lifespan
    dependencies.setup(app, pool, redis, settings)
    return app


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
