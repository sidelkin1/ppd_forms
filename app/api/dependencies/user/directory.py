from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.auth import UserDep
from app.api.dependencies.settings import SettingsDep


def user_directory_provider() -> Path:
    raise NotImplementedError


async def get_or_create_directory(
    user: UserDep, settings: SettingsDep
) -> Path:
    directory = settings.file_dir / user.username
    directory.mkdir(parents=True, exist_ok=True)
    return directory


UserDirDep = Annotated[Path, Depends(user_directory_provider)]
