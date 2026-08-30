import logging
import mimetypes
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination

from app.api import dependencies, endpoints, middlewares
from app.api.config.main import get_api_settings, get_auth_settings
from app.common.config.main import get_paths
from app.core.config.main import get_app_settings
from app.infrastructure.db.config.main import get_postgres_settings
from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.db.factories.local import (
    create_engine as create_local_engine,
)
from app.infrastructure.db.factories.local import (
    create_session_maker as create_local_session_maker,
)
from app.infrastructure.redis.config.main import get_redis_settings
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.infrastructure.sessions import Sessions
from app.initial_data import initialize_mapper

mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")

logger = logging.getLogger(__name__)


async def init_mapper(settings: PostgresSettings) -> None:
    """Инициализирует мапперы во временном пуле и освобождает его.

    Web-процесс не использует `Sessions` для обработки запросов, поэтому
    пул здесь одноразовый: создали -> загрузили мапперы -> dispose.
    """
    sessions = Sessions.create(local_settings=settings)
    try:
        await initialize_mapper(sessions)
    finally:
        await sessions.dispose()


def init_api() -> FastAPI:
    postgres_config = get_postgres_settings()
    engine = create_local_engine(postgres_config)
    pool = create_local_session_maker(engine)
    redis_config = get_redis_settings()
    redis = create_redis_pool(redis_config)
    app_config = get_app_settings()
    paths = get_paths()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("App started")
        yield
        # Redis-maker не требует закрытия: соединение открывается
        # на каждый запрос и закрывается в RedisProvider.dao().
        await engine.dispose()
        logger.info("App stopped")

    app = FastAPI(
        title=app_config.title,
        description=app_config.description,
        root_path=app_config.root_path,
        lifespan=lifespan,
    )
    add_pagination(app)
    endpoints.setup(app)
    middlewares.setup(app)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.mount(
        "/help",
        StaticFiles(directory=str(paths.site_dir), html=True),
        name="help",
    )
    auth_config = get_auth_settings()
    dependencies.setup(app, pool, redis, app_config, auth_config, paths)
    logger.info("App prepared")
    return app


async def run_api(app: FastAPI, log_level: str) -> None:
    api_config = get_api_settings()
    config = uvicorn.Config(
        app,
        host=api_config.host,
        port=api_config.port,
        log_level=logging.getLevelName(log_level),
        log_config=None,
    )
    server = uvicorn.Server(config)
    logger.info("Running API")
    await server.serve()
