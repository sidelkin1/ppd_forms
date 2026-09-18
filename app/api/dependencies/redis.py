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
    def __init__(
        self,
        pool: redismaker[ArqRedis],
        expires: timedelta,
        abort_timeout: float,
    ) -> None:
        self.pool = pool
        self.expires = expires
        self.abort_timeout = abort_timeout

    async def dao(self) -> AsyncGenerator[ArqDAO, None]:
        async with self.pool() as redis:
            yield ArqDAO(
                redis=redis,
                expires=self.expires,
                abort_timeout=self.abort_timeout,
            )


RedisDep = Annotated[ArqDAO, Depends(redis_provider)]
