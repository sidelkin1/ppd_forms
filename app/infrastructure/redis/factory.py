from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import TypeVar

from arq import ArqRedis
from arq import create_pool as create_redis_pool
from arq.connections import RedisSettings

from app.core.config.settings import Settings

T = TypeVar("T")
redismaker = Callable[[], _AsyncGeneratorContextManager[T]]


def create_redis_maker(redis_settings: RedisSettings) -> redismaker[ArqRedis]:
    @asynccontextmanager
    async def decorator() -> AsyncGenerator[ArqRedis, None]:
        redis = await create_redis_pool(redis_settings)
        try:
            yield redis
        finally:
            await redis.close()

    return decorator


def create_pool(settings: Settings) -> redismaker[ArqRedis]:
    return create_redis_maker(settings.redis_settings)
