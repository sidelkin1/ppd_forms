from collections.abc import AsyncGenerator
from datetime import timedelta
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends

from app.infrastructure.redis.dao import ArqDAO
from app.infrastructure.redis.factory import redismaker


def redis_provider() -> ArqDAO:
    raise NotImplementedError


class RedisProvider:
    def __init__(self, pool: redismaker[ArqRedis], expires: timedelta) -> None:
        self.pool = pool
        self.expires = expires

    async def dao(self) -> AsyncGenerator[ArqDAO, None]:
        async with self.pool() as redis:
            yield ArqDAO(redis=redis, expires=self.expires)


RedisDep = Annotated[ArqDAO, Depends(redis_provider)]
