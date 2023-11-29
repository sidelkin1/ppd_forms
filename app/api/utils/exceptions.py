from app.core.models.enums import JobStatus


class JobStatusException(Exception):
    def __init__(
        self,
        status: JobStatus | None = None,
        message: str | None = None,
    ) -> None:
        self.status = status
        self.message = message


class JobNotFoundError(JobStatusException):
    pass


class JobExecutionError(JobStatusException):
    pass


class JobWebSocketError(Exception):
    pass
