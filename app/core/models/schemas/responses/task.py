from pathlib import Path
from typing import TypeVar

from app.core.config.settings import settings
from app.core.models.dto import TaskBase
from app.core.models.schemas.responses.base import BaseResponse

TaskT = TypeVar("TaskT", bound=TaskBase, covariant=True, contravariant=False)


class TaskResponse(BaseResponse[TaskT]):
    @property
    def user_dir(self) -> Path:
        if self.job.user_id is None:
            raise ValueError("user_id must be set")
        directory = settings.file_dir / self.job.user_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def upload_dir(self) -> Path:
        directory = self.user_dir / "uploads"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @property
    def result_dir(self) -> Path:
        directory = self.user_dir / "results"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
