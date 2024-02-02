from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.auth import UserDep
from app.api.dependencies.settings import SettingsDep


def user_file_provider() -> Path:
    raise NotImplementedError


async def get_file_path(
    file_id: str, user: UserDep, settings: SettingsDep
) -> Path:
    results_dir = settings.file_dir / user.username / "results"
    return (results_dir / file_id).with_suffix(".csv")


UserFileDep = Annotated[Path, Depends(user_file_provider)]
