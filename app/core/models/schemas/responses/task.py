from pathlib import Path
from typing import TypeVar

from app.core.models.dto import TaskBase
from app.core.models.schemas.responses.base import BaseResponse

TaskT = TypeVar("TaskT", bound=TaskBase, covariant=True, contravariant=False)


class TaskResponse(BaseResponse[TaskT]):
    _file_dir: Path

    def __init__(self, _file_dir: Path, **data):
        super().__init__(**data)
        self._file_dir = _file_dir

    @property
    def user_dir(self) -> Path:
        if self.job.user_id is None:
            raise ValueError("user_id must be set")
        directory = self._file_dir / self.job.user_id
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
