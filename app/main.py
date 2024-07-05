import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import dependencies, endpoints, middlewares
from app.api.config.main import get_api_settings, get_auth_settings
from app.api.dependencies.db import DbProvider
from app.common.config.main import get_paths
from app.core.config.main import get_app_settings
from app.infrastructure.db.config.main import get_postgres_settings
from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.config.main import get_redis_settings
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.initial_data import initialize_mapper

logger = logging.getLogger(__name__)


async def init_mapper(settings: PostgresSettings) -> None:
    pool = create_local_pool(settings)
    provider = DbProvider(local_pool=pool)
    await initialize_mapper(provider)


def init_api() -> FastAPI:
    postgres_config = get_postgres_settings()
    pool = create_local_pool(postgres_config)
    redis_config = get_redis_settings()
    redis = create_redis_pool(redis_config)
    app_config = get_app_settings()
    app = FastAPI(title=app_config.title, description=app_config.description)
    endpoints.setup(app)
    middlewares.setup(app)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    auth_config = get_auth_settings()
    paths = get_paths()
    dependencies.setup(app, pool, redis, auth_config, paths)
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
