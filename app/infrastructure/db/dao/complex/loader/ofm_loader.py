from dataclasses import dataclass
from typing import TypeVar

from app.infrastructure.db.dao.complex import ofm
from app.infrastructure.db.dao.complex.loader.base import (
    BaseLoader,
    DestinationDAO,
)

SourceDAO = TypeVar(
    "SourceDAO", bound=ofm.BaseDAO, covariant=True, contravariant=False
)


@dataclass
class OfmLoader(BaseLoader[SourceDAO, DestinationDAO]):
    async def refresh(self, **params) -> None:
        objs = await self.src.get_by_params(**params)
        await self.dst.refresh(objs)
        await self.commit()

    async def reload(self, **params) -> None:
        objs = await self.src.get_by_params(**params)
        await self.dst.reload(objs)
        await self.commit()
