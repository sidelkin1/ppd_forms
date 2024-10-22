import asyncio
import logging
from typing import Annotated, Self

from fastapi import Depends, WebSocket

from app.api.dependencies.job import CurrentJobDep, JobResponseDep
from app.core.models.enums import JobStatus

logger = logging.getLogger(__name__)


class JobTracker:
    def __init__(
        self,
        websocket: WebSocket,
        job: CurrentJobDep,
        response: JobResponseDep,
        abort_on_disconnect: bool = False,
    ) -> None:
        self.websocket = websocket
        self.job = job
        self.response = response
        self.abort_on_disconnect = abort_on_disconnect

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

    async def _job_result(self) -> None:
        if self.response.job.status is JobStatus.not_found:
            self.response.job.message = "Job is not found"
            return
        try:
            await self.job.result()
        except Exception as error:
            self.response.job.status = JobStatus.error
            self.response.job.message = str(error)
            logger.error("Job error", exc_info=error)
        else:
            self.response.job.status = JobStatus.completed
            self.response.job.message = "Job is completed"

    async def send_response(self) -> None:
        await self.websocket.send_json(
            self.response.model_dump(mode="json", exclude_none=True)
        )

    async def status(self) -> None:
        await asyncio.wait(
            (self.socket_task, self.job_task),
            return_when=asyncio.FIRST_COMPLETED,
        )
        if self.socket_task.done():
            if self.abort_on_disconnect:
                logger.info(
                    "Websocket was closed, the job %s will be aborted",
                    self.response.job.job_id,
                )
                try:
                    await self.job.abort()
                except Exception as error:
                    logger.error(
                        "Exception while aborting job", exc_info=error
                    )
            else:
                logger.info(
                    "Websocket was closed, but the job will continue to run"
                )
        else:
            await self.send_response()


def get_job_tracker() -> JobTracker:
    raise NotImplementedError


JobTrackerDep = Annotated[JobTracker, Depends(get_job_tracker)]
