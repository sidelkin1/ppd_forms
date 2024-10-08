from typing import Annotated

from fastapi import Depends, Query
from fastapi_pagination import Params

PageNumber = Annotated[int, Query(ge=1, description="Page number")]


def get_pagination_params(page: PageNumber = 1) -> Params:
    raise NotImplementedError


class PageSize:
    def __init__(self, size: int):
        self.size = size

    async def __call__(self, page: PageNumber = 1) -> Params:
        return Params(page=page, size=self.size)


PageParamsDep = Annotated[Params, Depends(get_pagination_params)]
