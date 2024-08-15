from collections.abc import AsyncGenerator
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends

from app.infrastructure.redis.dao import ArqDAO
from app.infrastructure.redis.factory import redismaker


def redis_provider() -> ArqDAO:
    raise NotImplementedError


class RedisProvider:
    def __init__(self, pool: redismaker[ArqRedis]) -> None:
        self.pool = pool

    async def dao(self) -> AsyncGenerator[ArqDAO, None]:
        async with self.pool() as redis:
            yield ArqDAO(redis=redis)


RedisDep = Annotated[ArqDAO, Depends(redis_provider)]
