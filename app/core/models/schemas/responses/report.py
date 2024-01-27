from pathlib import Path
from typing import TypeVar

from app.core.models.dto import TaskOilLoss, TaskReport
from app.core.models.schemas.responses.task import TaskResponse

TaskT = TypeVar(
    "TaskT", bound=TaskReport
)  # FIXME need covariant, contrvariant values


class BaseReportResponse(TaskResponse[TaskT]):
    @property
    def path(self) -> Path:
        if self.job.file_id is None:
            raise ValueError("file_id must be set")
        return (self.result_dir / self.job.file_id).with_suffix(".csv")


ReportResponse = BaseReportResponse[TaskReport]
OilLossResponse = BaseReportResponse[TaskOilLoss]
