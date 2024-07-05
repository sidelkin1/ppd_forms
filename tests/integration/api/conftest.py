from collections.abc import AsyncGenerator, Callable, Generator

import pytest
import pytest_asyncio
from arq.connections import ArqRedis
from arq.worker import Worker
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.api import dependencies, endpoints, middlewares
from app.api.config.models.auth import AuthSettings
from app.api.dependencies.auth import AuthProvider
from app.api.models.auth import Token, User
from app.common.config.models.paths import Paths
from app.infrastructure.db.config.models.local import PostgresSettings
from app.infrastructure.db.factories.local import (
    create_pool as create_local_pool,
)
from app.infrastructure.redis.config.models.redis import RedisSettings
from app.infrastructure.redis.factory import create_pool as create_redis_pool
from tests.fixtures.task_fixtures import (  # noqa
    date_range,
    matrix_effect,
    task_database,
    task_excel,
    task_inj_loss,
    task_matrix,
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
def test_client(
    app: FastAPI, token: Token
) -> Generator[TestClient, None, None]:
    with TestClient(
        app=app,
        base_url="http://test",
        cookies={"access_token": f"Bearer {token.access_token}"},
    ) as client:
        yield client


@pytest.fixture(scope="session")
def anon_test_client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def app(
    postgres_config: PostgresSettings,
    redis_config: RedisSettings,
    auth_config: AuthSettings,
    paths: Paths,
) -> FastAPI:
    pool = create_local_pool(postgres_config)
    redis = create_redis_pool(redis_config)
    app = FastAPI()
    endpoints.setup(app)
    middlewares.setup(app)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    dependencies.setup(app, pool, redis, auth_config, paths)
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
def auth(auth_config: AuthSettings) -> AuthProvider:
    return AuthProvider(auth_config)


@pytest.fixture(scope="session")
def user() -> User:
    return User(username="test_user")


@pytest.fixture(scope="session")
def token(user: User, auth: AuthProvider) -> Token:
    return auth.create_user_token(user)
