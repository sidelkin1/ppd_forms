from dataclasses import dataclass
from typing import TypeVar

from app.infrastructure.db.dao import excel
from app.infrastructure.db.dao.complex.loader.base import (
    BaseLoader,
    DestinationDAO,
)

SourceDAO = TypeVar(
    "SourceDAO", bound=excel.BaseDAO, covariant=True, contravariant=False
)


@dataclass
class ExcelLoader(BaseLoader[SourceDAO, DestinationDAO]):
    async def refresh(self) -> None:
        objs = await self.src.get_all()
        await self.dst.refresh(objs)
        await self.commit()

    async def reload(self) -> None:
        objs = await self.src.get_all()
        await self.dst.reload(objs)
        await self.commit()
