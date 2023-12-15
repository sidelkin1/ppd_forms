from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.user.session import UserIdDep
from app.core.config.settings import settings


def user_file_provider() -> Path:
    raise NotImplementedError


async def get_file_path(file_id: str, user_id: UserIdDep) -> Path:
    results_dir = settings.file_dir / user_id / "results"
    return (results_dir / file_id).with_suffix(".csv")


UserFileDep = Annotated[Path, Depends(user_file_provider)]
