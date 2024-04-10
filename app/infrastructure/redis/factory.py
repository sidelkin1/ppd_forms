from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import TypeVar

from arq import ArqRedis
from arq import create_pool as create_redis_pool
from arq.connections import RedisSettings as ArqRedisSettings

from app.infrastructure.redis.config.main import RedisSettings

T = TypeVar("T")
redismaker = Callable[[], _AsyncGeneratorContextManager[T]]


def create_redis_maker(
    redis_settings: ArqRedisSettings,
) -> redismaker[ArqRedis]:
    @asynccontextmanager
    async def decorator() -> AsyncGenerator[ArqRedis, None]:
        redis = await create_redis_pool(redis_settings)
        try:
            yield redis
        finally:
            await redis.close()

    return decorator


def create_pool(settings: RedisSettings) -> redismaker[ArqRedis]:
    return create_redis_maker(settings.arq_settings)
