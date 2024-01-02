import asyncio
from collections.abc import AsyncGenerator
from typing import Annotated

from arq.jobs import Job
from fastapi import Depends, WebSocket

from app.api.dependencies.job import CurrentJobDep
from app.api.dependencies.responses import JobResponseDep
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
        await self.websocket.close()
        self.socket_task.cancel()
        self.job_task.cancel()

    async def _socket_listen(self) -> None:
        try:
            while True:
                await self.websocket.receive()
        except Exception as error:
            print(f"Webosocket error: {error}")  # TODO log

    async def _job_result(self) -> None:
        if self.response.job.status is JobStatus.not_found:
            self.response.job.message = "Job is not found"
            return
        try:
            await self.job.result()
        except Exception as error:
            self.response.job.status = JobStatus.error
            self.response.job.message = str(error)
            print(f"Job error: {error}")  # TODO log
        else:
            self.response.job.status = JobStatus.completed
            self.response.job.message = "Job is completed"

    async def send_response(self) -> None:
        await self.websocket.send_text(
            self.response.model_dump_json(exclude_none=True)
        )

    async def status(self) -> None:
        await asyncio.wait(
            (self.socket_task, self.job_task),
            return_when=asyncio.FIRST_COMPLETED,
        )
        if self.socket_task.done():
            try:
                await self.job.abort()
            except Exception:
                print("Exception while aborting job")  # TODO log
        else:
            await self.send_response()


def job_tracker_provider() -> JobTracker:
    raise NotImplementedError


async def get_job_tracker(
    websocket: WebSocket, job: CurrentJobDep, response: JobResponseDep
) -> AsyncGenerator[JobTracker, None]:
    async with JobTracker(websocket, job, response) as tracker:
        yield tracker


JobTrackerDep = Annotated[JobTracker, Depends(job_tracker_provider)]
