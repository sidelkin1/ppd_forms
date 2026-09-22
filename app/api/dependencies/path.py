from typing import Annotated

from fastapi import Depends

from app.common.paths import PathProvider


def get_path_provider() -> PathProvider:
    raise NotImplementedError


PathDep = Annotated[PathProvider, Depends(get_path_provider)]
