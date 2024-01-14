import os
from collections.abc import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from arq.connections import ArqRedis
from arq.worker import Worker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from httpx import AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.api import dependencies
from app.api.routes.routers import main_router
from app.core.config.settings import Settings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from app.lifespan import lifespan
from tests.fixtures.task_fixtures import (  # noqa
    task_database,
    task_excel,
    task_oil_loss,
    task_report,
)


@pytest_asyncio.fixture(scope="session")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app=app, base_url="http://test") as client:
        yield client


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
