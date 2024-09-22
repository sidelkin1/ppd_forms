from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import Params


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
) -> Params:
    raise NotImplementedError


class PageSize:
    def __init__(self, size: int):
        self.size = size

    async def __call__(
        self, page: int = Query(1, ge=1, description="Page number")
    ) -> Params:
        return Params(page=page, size=self.size)


PageParamsDeps = Annotated[Params, Depends(get_pagination_params)]
