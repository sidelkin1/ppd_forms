import asyncio
import logging
from typing import Annotated, Self

from fastapi import Depends, WebSocket

from app.api.dependencies.auth import UserDep
from app.api.dependencies.redis import RedisDep
from app.api.models.responses import JobResponse

logger = logging.getLogger(__name__)


class JobTracker:
    def __init__(
        self, job_id: str, user: UserDep, websocket: WebSocket, redis: RedisDep
    ) -> None:
        self.job_id = job_id
        self.username = user.username
        self.websocket = websocket
        self.redis = redis

    async def __aenter__(self) -> Self:
        await self.websocket.accept()
        self.socket_task = asyncio.create_task(self._socket_listen())
        self.job_task = asyncio.create_task(self._job_result())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.socket_task.cancel()
        self.job_task.cancel()

    async def _socket_listen(self) -> None:
        try:
            while True:
                await self.websocket.receive()
        except Exception as error:
            logger.error("Websocket error", exc_info=error)

    async def _job_result(self) -> JobResponse:
        try:
            await self.redis.result(self.job_id, self.username)
        except asyncio.CancelledError:
            logger.info("Job %s was cancelled", self.job_id)
        except Exception as error:
            logger.error("Job error", exc_info=error)
        return await self.redis.response(self.job_id, self.username)

    async def send_response(self, response: JobResponse) -> None:
        await self.websocket.send_json(
            response.model_dump(mode="json", exclude_none=True)
        )

    async def status(self) -> None:
        await asyncio.wait(
            (self.socket_task, self.job_task),
            return_when=asyncio.FIRST_COMPLETED,
        )
        if self.socket_task.done():
            logger.info(
                "Websocket was closed, but the job will continue to run"
            )
        else:
            await self.send_response(self.job_task.result())


def get_job_tracker() -> JobTracker:
    raise NotImplementedError


JobTrackerDep = Annotated[JobTracker, Depends(get_job_tracker)]
