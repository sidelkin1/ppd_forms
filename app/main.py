import logging
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api import dependencies
from app.api.routes.routers import main_router
from app.core.config.parsers.logging_config import setup_logging
from app.core.config.settings import get_settings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.lifespan import lifespan

logger = logging.getLogger(__name__)


def main() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.logging_config_file)
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

    logger.info("app prepared")
    return app


def run() -> None:
    uvicorn.run("app.main:main", factory=True)


if __name__ == "__main__":
    run()
