from pathlib import Path

from app.core.models.dto import TaskReport
from app.core.models.schemas.responses.task import TaskResponse


class ReportResponse(TaskResponse[TaskReport]):
    @property
    def path(self) -> Path:
        if self.job.file_id is None:
            raise ValueError("file_id must be set")
        return (self.result_dir / self.job.file_id).with_suffix(".csv")
