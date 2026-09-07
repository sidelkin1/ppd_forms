from dataclasses import dataclass
from typing import TypeVar

from app.infrastructure.db.dao.complex.loaders.base import (
    BaseLoader,
    DestinationDAO,
)
from app.infrastructure.files.dao.csv.base import BaseDAO as CsvDAO

SourceDAO = TypeVar(
    "SourceDAO", bound=CsvDAO, covariant=True, contravariant=False
)


@dataclass
class CsvLoader(BaseLoader[SourceDAO, DestinationDAO]):
    async def refresh(self) -> None:
        objs = await self.src.get_all()
        await self.dst.refresh(objs)
        await self.commit()

    async def reload(self) -> None:
        objs = await self.src.get_all()
        await self.dst.reload(objs)
        await self.commit()
