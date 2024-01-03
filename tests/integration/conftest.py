import os
from collections.abc import Generator
from typing import Callable

import pytest
import pytest_asyncio
from arq.connections import ArqRedis
from arq.worker import Worker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from app.api import dependencies
from app.api.routes.routers import main_router
from app.core.config.settings import settings
from app.infrastructure.arq.factory import create_pool as create_redis_pool
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.lifespan import lifespan
from tests.fixtures.job_fixtures import job_abort  # noqa: F401
from tests.fixtures.job_fixtures import job_error  # noqa: F401
from tests.fixtures.job_fixtures import job_ok  # noqa: F401
from tests.fixtures.response_fixtures import test_response  # noqa: F401
from tests.fixtures.response_fixtures import test_response_error  # noqa: F401
from tests.fixtures.response_fixtures import test_response_ok  # noqa: F401


@pytest_asyncio.fixture(scope="session")
async def arq_redis() -> ArqRedis:
    redis_ = ArqRedis(host="localhost", port=6379, encoding="utf-8")
    await redis_.flushall()
    yield redis_
    await redis_.close(close_connection_pool=True)


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
    ):
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
def app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        lifespan=lifespan,
    )
    app.state.pool = create_local_pool(settings)
    app.state.redis = create_redis_pool(settings)
    app.add_middleware(SessionMiddleware, secret_key=os.urandom(32))
    app.include_router(main_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    dependencies.setup(app)
    return app


@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app=app, base_url="http://test") as client:
        yield client
