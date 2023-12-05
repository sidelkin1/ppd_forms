from dataclasses import dataclass
from typing import TypeVar

from app.infrastructure.db.dao.complex.loader.base import (
    BaseLoader,
    DestinationDAO,
)
from app.infrastructure.file.dao.excel.base import BaseDAO

SourceDAO = TypeVar(
    "SourceDAO", bound=BaseDAO, covariant=True, contravariant=False
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
