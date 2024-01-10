import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api import dependencies
from app.api.routes.routers import main_router
from app.core.config.settings import settings
from app.infrastructure.arq.factory import create_pool as create_redis_pool
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.db.factories.ofm import create_pool as create_ofm_pool
from app.infrastructure.db.models import ofm
from app.lifespan import lifespan


def main() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        lifespan=lifespan,
    )
    app.state.pool = create_local_pool(settings)
    app.state.redis = create_redis_pool(settings)
    app.state.ofm = create_ofm_pool(settings) if ofm.setup(settings) else None
    app.add_middleware(SessionMiddleware, secret_key=os.urandom(32))
    app.include_router(main_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    dependencies.setup(app)

    return app


def run() -> None:
    uvicorn.run("app.main:main", factory=True)


if __name__ == "__main__":
    run()
