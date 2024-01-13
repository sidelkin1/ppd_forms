from collections.abc import AsyncGenerator
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends

from app.infrastructure.redis.dao import RedisDAO


def redis_provider() -> RedisDAO:
    raise NotImplementedError


class RedisProvider:
    def __init__(self, pool: ArqRedis) -> None:
        self.pool = pool

    async def dao(self) -> AsyncGenerator[RedisDAO, None]:
        async with self.pool() as redis:
            yield RedisDAO(redis=redis)


RedisDep = Annotated[RedisDAO, Depends(redis_provider)]
