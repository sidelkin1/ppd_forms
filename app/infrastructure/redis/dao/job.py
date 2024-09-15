from datetime import timedelta

from redis.asyncio.client import Redis

from app.api.models.responses import BaseResponse, JobResponse


class ScheduledJobsDAO:
    def __init__(
        self,
        redis: Redis,
        prefix: str = "scheduled:jobs",
        expires: timedelta = timedelta(days=1),
    ):
        self.redis = redis
        self.prefix = prefix
        self.expires = expires

    def _create_key(self, username: str, job_id: str) -> str:
        return f"{self.prefix}:{username}:{job_id}"

    async def add_job(self, username: str, response: BaseResponse):
        key = self._create_key(username, response.job.job_id)
        await self.redis.setex(key, self.expires, response.model_dump_json())

    async def get_jobs(self, username: str) -> list[JobResponse]:
        pattern = self._create_key(username, "*")
        keys = await self.redis.keys(pattern)
        objs = []
        for key in keys:
            obj_data = await self.redis.get(key)
            if obj_data:
                response = JobResponse.model_validate_json(obj_data)
                objs.append(response)
        return objs
