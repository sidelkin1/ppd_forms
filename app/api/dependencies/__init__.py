from arq import ArqRedis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.config.models.auth import AuthSettings
from app.common.config.models.paths import Paths
from app.core.config.models.app import AppSettings
from app.infrastructure.redis.factory import redismaker

from .auth import (
    AuthProvider,
    get_auth_provider,
    get_current_user,
    get_current_user_or_none,
)
from .db import DbProvider, dao_provider
from .job import (
    JobProvider,
    get_current_job,
    get_job_provider,
    get_job_reponse,
    get_new_job,
)
from .pagination import PageSize, get_pagination_params
from .path import PathProvider, get_path_provider
from .redis import RedisProvider, redis_provider
from .tracker import JobTracker, get_job_tracker


def setup(
    app: FastAPI,
    pool: async_sessionmaker[AsyncSession],
    redis: redismaker[ArqRedis],
    app_config: AppSettings,
    auth_config: AuthSettings,
    paths: Paths,
) -> None:
    app.dependency_overrides[dao_provider] = DbProvider(pool).dao
    app.dependency_overrides[redis_provider] = RedisProvider(
        pool=redis, expires=app_config.keep_result
    ).dao

    path_provider = PathProvider(paths)
    app.dependency_overrides[get_path_provider] = lambda: path_provider

    auth_provider = AuthProvider(auth_config)
    app.dependency_overrides[get_current_user] = auth_provider.get_current_user
    app.dependency_overrides[get_current_user_or_none] = (
        auth_provider.get_current_user_or_none
    )
    app.dependency_overrides[get_auth_provider] = lambda: auth_provider

    job_provider = JobProvider()
    app.dependency_overrides[get_new_job] = job_provider.create
    app.dependency_overrides[get_current_job] = job_provider.current
    app.dependency_overrides[get_job_reponse] = job_provider.response
    app.dependency_overrides[get_job_provider] = lambda: job_provider
    app.dependency_overrides[get_job_tracker] = JobTracker

    app.dependency_overrides[get_pagination_params] = PageSize(
        app_config.page_size
    )
