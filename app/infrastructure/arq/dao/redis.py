from arq import ArqRedis
from arq.jobs import Job
from pydantic import BaseModel

from app.core.models.dto import JobStamp


class RedisDAO:
    def __init__(self, redis: ArqRedis):
        self.redis = redis

    async def enqueue_job(self, func: str, *args, **kwargs) -> Job | None:
        return await self.redis.enqueue_job(func, *args, **kwargs)

    async def enqueue_task(
        self, task: BaseModel, job_stamp: JobStamp
    ) -> Job | None:
        return await self.redis.enqueue_job(
            "perform_work", task, job_stamp, _job_id=job_stamp.job_id
        )
