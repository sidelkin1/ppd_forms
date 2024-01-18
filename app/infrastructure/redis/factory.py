from contextlib import asynccontextmanager

from arq import ArqRedis
from arq import create_pool as create_redis_pool
from arq.connections import RedisSettings

from app.core.config.settings import Settings


def create_redis_maker(redis_settings: RedisSettings):
    @asynccontextmanager
    async def decorator():
        redis = await create_redis_pool(redis_settings)
        try:
            yield redis
        finally:
            await redis.aclose()

    return decorator


def create_pool(settings: Settings) -> ArqRedis:
    return create_redis_maker(settings.redis_settings)
