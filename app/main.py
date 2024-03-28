import logging

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import dependencies, endpoints, middlewares
from app.api.dependencies.db import DbProvider
from app.core.config.settings import Settings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.initial_data import initialize_mapper

logger = logging.getLogger(__name__)


async def init_mapper(settings: Settings) -> None:
    pool = create_local_pool(settings)
    provider = DbProvider(local_pool=pool)
    await initialize_mapper(provider)


def init_api(settings: Settings) -> FastAPI:
    pool = create_local_pool(settings)
    redis = create_redis_pool(settings)
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
    )
    endpoints.setup(app)
    middlewares.setup(app)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    dependencies.setup(app, pool, redis, settings)
    logger.info("App prepared")
    return app


async def run_api(app: FastAPI, settings: Settings) -> None:
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=logging.getLevelName(settings.log_level),
        log_config=None,
    )
    server = uvicorn.Server(config)
    logger.info("Running API")
    await server.serve()
