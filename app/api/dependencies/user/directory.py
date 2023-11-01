from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.user.session import UserIdDep
from app.core.utils.result_path import result_path


def user_directory_provider() -> Path:
    raise NotImplementedError


async def get_or_create_directory(user_id: UserIdDep) -> Path:
    directory = result_path(user_id)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    return directory


UserDirDep = Annotated[Path, Depends(user_directory_provider)]
