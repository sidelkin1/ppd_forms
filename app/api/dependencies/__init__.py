from arq import ArqRedis
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.dependencies.db import DbProvider, dao_provider
from app.api.dependencies.path import PathProvider, get_path_provider
from app.api.dependencies.redis import RedisProvider, redis_provider
from app.api.dependencies.session import (
    get_or_create_user_id,
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

    path_provider = PathProvider(settings)
    app.dependency_overrides[get_path_provider] = lambda: path_provider

    app.dependency_overrides[user_id_provider] = get_or_create_user_id
