from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.dependencies.user.session import UserIdDep
from app.core.utils.result_path import result_path


def user_file_provider() -> Path:
    raise NotImplementedError


async def get_or_create_path(file_id: str, user_id: UserIdDep) -> Path:
    return result_path(user_id, file_id)


FilePathDep = Annotated[Path, Depends(user_file_provider)]
