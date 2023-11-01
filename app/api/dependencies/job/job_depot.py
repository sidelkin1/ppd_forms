from asyncio import Task, create_task
from typing import Annotated, Callable

from arq.jobs import Job
from fastapi import Depends

from app.api.dependencies.redis.provider import RedisDep
from app.infrastructure.arq.dao.redis import RedisDAO


class JobDepot:
    def __init__(self, redis: RedisDAO):
        self.redis = redis

    async def __aenter__(self):
        self._tasks: list[Task] = []
        self._jobs: list[Job] = []
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        while self._tasks:
            self._tasks.pop().cancel()
        while self._jobs:
            try:
                await self._jobs.pop().abort()
            except Exception:
                print("Exception while aborting job")  # TODO log

    def add_task(self, func: Callable, *args, **kwargs) -> Task:
        task = create_task(func(*args, **kwargs))
        self._tasks.append(task)
        return task

    async def add_job(self, func: str, *args, **kwargs) -> Job:
        job = await self.redis.enqueue_job(func, *args, **kwargs)
        self._jobs.append(job)
        return job


def job_depot_provider() -> JobDepot:
    raise NotImplementedError


async def get_job_depot(redis: RedisDep):
    async with JobDepot(redis) as job_depot:
        yield job_depot


JobDepotDep = Annotated[JobDepot, Depends(job_depot_provider)]
