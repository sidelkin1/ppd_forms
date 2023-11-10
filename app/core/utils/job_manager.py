from typing import Any

from fastapi import WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.websockets import WebSocketState
from pydantic import ValidationError

from app.api.dependencies.job.job_depot import JobDepot
from app.core.models.dto.jobs.job_stamp import JobStamp
from app.core.models.dto.tasks import task_holder
from app.core.models.enums import JobStatus, TaskId
from app.core.utils.exceptions import (
    DataModelValidationError,
    JobExecutionError,
    JobStatusException,
    TaskIdNotFoundError,
    TaskIdValueError,
)


class JobManager:
    def __init__(
        self,
        websocket: WebSocket,
        job_depot: JobDepot,
        user_id: str,
        data: dict[str, Any],
    ) -> None:
        self.websocket = websocket
        self.job_depot = job_depot
        self.job_stamp = JobStamp(user_id=user_id, data=data)

    async def __aenter__(self):
        await self.send_job_stamp()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if any(
            (
                isinstance(
                    exc_value, (WebSocketException, WebSocketDisconnect)
                ),
                self.websocket.client_state != WebSocketState.CONNECTED,
                self.websocket.application_state != WebSocketState.CONNECTED,
            )
        ):
            print("WebSocket connection error")  # TODO log
            return
        if isinstance(exc_value, JobStatusException):
            await self.send_job_stamp(
                status=exc_value.status,
                message=exc_value.message,
            )
            return
        if exc_value:
            await self.send_job_stamp(
                status=JobStatus.execution_error,
                message=str(exc_value),
            )
            return
        await self.send_job_stamp(status=JobStatus.completed)

    async def send_job_stamp(
        self,
        status: JobStatus | None = None,
        message: str | None = None,
    ) -> None:
        if status is not None:
            self.job_stamp.status = status
        if message is not None:
            self.job_stamp.message = message
        await self.websocket.send_json(
            self.job_stamp.model_dump_json(exclude_none=True)
        )

    async def enqueue_job(self) -> None:
        if "task_id" not in self.job_stamp.data:
            raise TaskIdNotFoundError(
                status=JobStatus.data_error,
                message="Нет обязательного поля `task_id`!",
            )

        try:
            TaskId[self.job_stamp.data["task_id"]]
        except ValueError as error:
            raise TaskIdValueError(
                status=JobStatus.data_error,
                message="Некорректное значение поля `task_id`!",
            ) from error

        try:
            task = task_holder.to_dto(self.job_stamp.data)
        except ValidationError as error:
            raise DataModelValidationError(
                status=JobStatus.data_error,
                message=str(error),
            ) from error

        job = await self.job_depot.add_job(
            "perform_work", task, self.job_stamp, _job_id=self.job_stamp.job_id
        )

        try:
            await job.result()
        except Exception as error:
            raise JobExecutionError(
                status=JobStatus.execution_error,
                message=str(error),
            ) from error
