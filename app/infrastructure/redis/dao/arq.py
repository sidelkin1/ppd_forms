from typing import Any

import structlog
from arq import ArqRedis
from arq.jobs import Job

from app.api.models.responses import BaseResponse, JobResponse
from app.core.models.enums.task_id import TaskId
from app.infrastructure.redis.dao.job import ScheduledJobsDAO


class ArqDAO:
    def __init__(self, redis: ArqRedis):
        self.redis = redis
        self.schedule = ScheduledJobsDAO(redis)

    async def enqueue_task(
        self, response: BaseResponse, username: str
    ) -> Job | None:
        ctx = structlog.contextvars.get_contextvars()
        job = await self.redis.enqueue_job(
            "perform_work", response, ctx, _job_id=response.job.job_id
        )
        await self.schedule.add_job(username, response)
        return job

    async def result(self, response: BaseResponse, username: str) -> Any:
        job = await self.enqueue_task(response, username)
        return await job.result()

    async def get_scheduled_tasks(
        self, username: str, task_id: TaskId | None = None
    ) -> list[JobResponse]:
        responses = await self.schedule.get_jobs(username)
        if task_id:
            return [
                response
                for response in responses
                if response.task.get("task_id") == task_id
            ]
        return responses
