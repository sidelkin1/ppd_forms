from typing import Annotated

from fastapi import Depends

from app.common.config.models.paths import Paths


def get_path_provider() -> Paths:
    raise NotImplementedError


PathDep = Annotated[Paths, Depends(get_path_provider)]
