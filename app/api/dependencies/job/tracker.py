import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated

from arq.jobs import Job
from fastapi import Depends, WebSocket

from app.api.dependencies.job import CurrentJobDep, JobResponseDep
from app.api.utils.exceptions import (
    JobExecutionError,
    JobNotFoundError,
    JobStatusException,
    JobWebSocketError,
)
from app.core.models.enums import JobStatus
from app.core.models.schemas import JobResponse


class JobTracker:
    def __init__(
        self, websocket: WebSocket, job: Job, response: JobResponse
    ) -> None:
        self.websocket = websocket
        self.job = job
        self.response = response

    async def __aenter__(self):
        await self.websocket.accept()
        self.socket_task = asyncio.create_task(self._socket_listen())
        self.job_task = asyncio.create_task(self._job_result())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if not self.socket_task.done():
            self.socket_task.cancel()
            await self.websocket.close()
        if not self.job_task.done():
            self.job_task.cancel()
            try:
                await self.job.abort()
            except Exception:
                print("Exception while aborting job")  # TODO log

    async def _socket_listen(self) -> None:
        while True:
            await self.websocket.receive()

    async def _job_result(self) -> None:
        await self.job.result()

    async def send_response(
        self,
        status: JobStatus | None = None,
        message: str | None = None,
    ) -> None:
        if status is not None:
            self.response.job.status = status
        if message is not None:
            self.response.job.message = message
        await self.websocket.send_text(
            self.response.model_dump_json(exclude_none=True)
        )

    async def status(self) -> None:
        try:
            if self.response.job.status is JobStatus.not_found:
                raise JobNotFoundError(message="Job is not found")
            await asyncio.wait(
                (self.socket_task, self.job_task),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if self.socket_task.done():
                error = self.socket_task.exception()
                raise JobWebSocketError(
                    f"Webosocket error: {error}"
                ) from error
            try:
                self.job_task.result()
            except Exception as error:
                raise JobExecutionError(
                    status=JobStatus.error,
                    message=str(error),
                ) from error
        except JobWebSocketError as error:
            print(error)  # TODO log
        except JobStatusException as error:
            await self.send_response(
                status=error.status, message=error.message
            )
        except Exception as error:
            await self.send_response(
                status=JobStatus.error, message=str(error)
            )
        else:
            await self.send_response(
                status=JobStatus.completed, message="Job is completed"
            )


def job_tracker_provider() -> JobTracker:
    raise NotImplementedError


async def get_job_tracker(
    websocket: WebSocket, job: CurrentJobDep, response: JobResponseDep
) -> AsyncGenerator[JobTracker, None]:
    async with JobTracker(websocket, job, response) as tracker:
        yield tracker


JobTrackerDep = Annotated[JobTracker, Depends(job_tracker_provider)]
