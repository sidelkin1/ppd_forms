from collections.abc import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from arq.connections import ArqRedis
from arq.worker import Worker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api import dependencies
from app.api.dependencies.auth import AuthProvider
from app.api.models.auth import Token
from app.api.models.user import User
from app.api.routes.routers import main_router
from app.core.config.settings import Settings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from tests.fixtures.task_fixtures import (  # noqa
    task_database,
    task_excel,
    task_oil_loss,
    task_report,
)
from tests.fixtures.worker_fixtures import (  # noqa
    work_error,
    work_long,
    work_ok,
    work_uneft,
)


@pytest_asyncio.fixture(scope="session")
async def client(
    app: FastAPI, token: Token
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app,
        base_url="http://test",
        cookies={"access_token": f"Bearer {token.access_token}"},
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def anon_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
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
    app = FastAPI()
    app.include_router(main_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    dependencies.setup(app, pool, redis, settings)
    return app


@pytest_asyncio.fixture
async def worker(
    arq_redis: ArqRedis,
) -> AsyncGenerator[Callable[..., Worker], None]:
    worker_: Worker | None = None

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
def auth(settings: Settings) -> AuthProvider:
    return AuthProvider(settings)


@pytest.fixture(scope="session")
def user() -> User:
    return User(username="test_user")


@pytest.fixture(scope="session")
def token(user: User, auth: AuthProvider) -> Token:
    return auth.create_user_token(user)
