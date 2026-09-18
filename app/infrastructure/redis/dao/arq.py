import asyncio
from datetime import timedelta
from typing import Any

import structlog
from arq import ArqRedis
from arq.jobs import Job, JobResult, ResultNotFound

from app.api.models.responses import BaseResponse, JobResponse
from app.core.models.enums import JobStatus
from app.core.models.enums.task_id import TaskId
from app.infrastructure.redis.dao.job import ScheduledJobsDAO


# TODO(layers/A): infra must not import app.api - move the JobRequest
# envelope to core/models/dto. See cancel-job-plan.md.
class ArqDAO:
    def __init__(
        self, redis: ArqRedis, expires: timedelta, abort_timeout: float
    ):
        self.redis = redis
        self.abort_timeout = abort_timeout
        self.schedule = ScheduledJobsDAO(redis, expires=expires)

    async def enqueue_task(
        self, response: BaseResponse, username: str
    ) -> None:
        ctx = structlog.contextvars.get_contextvars()
        await self.redis.enqueue_job(
            "perform_work", response, ctx, _job_id=response.job.job_id
        )
        await self.schedule.add_job(username, response)

    async def response(self, job_id: str, username: str) -> JobResponse:
        if not (response := await self.schedule.get_job(username, job_id)):
            return JobResponse.not_found(job_id)
        job = Job(job_id=job_id, redis=self.redis)
        status = JobStatus.from_arq(await job.status())
        info = await job.info()
        if isinstance(info, JobResult):
            if info.success:
                response.result = info.result
                response.job.status = JobStatus.completed
            elif isinstance(info.result, asyncio.CancelledError):
                response.job.status = JobStatus.cancelled
                response.job.message = "Job is cancelled"
            else:
                response.job.status = JobStatus.error
                response.job.message = str(info.result)
        else:
            response.job.status = status
        return response

    async def result(self, job_id: str, username: str) -> Any:
        if not await self.schedule.get_job(username, job_id):
            raise ResultNotFound(f"Задача {job_id} не найдена!")
        job = Job(job_id=job_id, redis=self.redis)
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
