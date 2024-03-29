from typing import Any

import structlog
from arq import ArqRedis
from arq.jobs import Job

from app.core.models.schemas import BaseResponse


class RedisDAO:
    def __init__(self, redis: ArqRedis):
        self.redis = redis

    async def enqueue_task(self, response: BaseResponse) -> Job | None:
        ctx = structlog.contextvars.get_contextvars()
        return await self.redis.enqueue_job(
            "perform_work", response, ctx, _job_id=response.job.job_id
        )

    async def result(self, response: BaseResponse) -> Any:
        job = await self.enqueue_task(response)
        return await job.result()
