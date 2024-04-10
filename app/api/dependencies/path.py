from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.infrastructure.files.config.models.paths import Paths


class PathProvider:
    def __init__(self, paths: Paths) -> None:
        self.file_dir = paths.file_dir
        self.report_config_file = paths.report_config
        self.table_config_file = paths.table_config

    def user_dir(self, user_id: str) -> Path:
        directory = self.file_dir / user_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def upload_dir(self, user_id: str) -> Path:
        return self.user_dir(user_id) / "uploads"

    def result_dir(self, user_id: str) -> Path:
        return self.user_dir(user_id) / "results"

    def file_path(self, user_id: str, file_id: str) -> Path:
        return (self.result_dir(user_id) / file_id).with_suffix(".csv")


def get_path_provider() -> PathProvider:
    raise NotImplementedError


PathDep = Annotated[PathProvider, Depends(get_path_provider)]
