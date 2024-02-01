from typing import Any

from arq import ArqRedis
from arq.jobs import Job

from app.core.models.schemas import BaseResponse


class RedisDAO:
    def __init__(self, redis: ArqRedis):
        self.redis = redis

    async def enqueue_task(self, response: BaseResponse) -> Job | None:
        return await self.redis.enqueue_job(
            "perform_work", response, _job_id=response.job.job_id
        )

    async def result(self, response: BaseResponse) -> Any:
        job = await self.enqueue_task(response)
        return await job.result()
