from pathlib import Path

from app.core.models.dto import TaskExcel
from app.core.models.schemas.responses.task import TaskResponse


class ExcelResponse(TaskResponse[TaskExcel]):
    @property
    def path(self) -> Path:
        return self.upload_dir / self.task.file
