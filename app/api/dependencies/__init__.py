from arq import ArqRedis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies.db import DbProvider, dao_provider
from app.api.dependencies.job import (
    create_job_stamp,
    current_job_provider,
    get_current_job,
    get_job_tracker,
    job_tracker_provider,
    new_job_provider,
)
from app.api.dependencies.redis import RedisProvider, redis_provider
from app.api.dependencies.response import (
    get_job_response,
    job_response_provider,
)
from app.api.dependencies.settings import settings_provider
from app.api.dependencies.user import (
    get_file_path,
    get_or_create_directory,
    get_or_create_user_id,
    user_directory_provider,
    user_file_provider,
    user_id_provider,
)
from app.core.config.settings import Settings
from app.infrastructure.redis.factory import redismaker


def setup(
    app: FastAPI,
    pool: async_sessionmaker[AsyncSession],
    redis: redismaker[ArqRedis],
    settings: Settings,
) -> None:
    app.dependency_overrides[dao_provider] = DbProvider(
        local_pool=pool
    ).local_dao
    app.dependency_overrides[redis_provider] = RedisProvider(pool=redis).dao
    app.dependency_overrides[settings_provider] = lambda: settings

    app.dependency_overrides[new_job_provider] = create_job_stamp
    app.dependency_overrides[current_job_provider] = get_current_job
    app.dependency_overrides[job_response_provider] = get_job_response
    app.dependency_overrides[job_tracker_provider] = get_job_tracker

    app.dependency_overrides[user_id_provider] = get_or_create_user_id
    app.dependency_overrides[user_directory_provider] = get_or_create_directory
    app.dependency_overrides[user_file_provider] = get_file_path
