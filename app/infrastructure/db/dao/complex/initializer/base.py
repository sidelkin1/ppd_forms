from dataclasses import dataclass
from typing import Generic, TypeVar

from app.infrastructure.db.dao import csv, local

SourceDAO = TypeVar(
    "SourceDAO", bound=csv.BaseDAO, covariant=True, contravariant=False
)
DestinationDAO = TypeVar(
    "DestinationDAO", bound=local.BaseDAO, covariant=True, contravariant=False
)


@dataclass
class BaseInitializer(Generic[SourceDAO, DestinationDAO]):
    src: SourceDAO
    dst: DestinationDAO

    async def initialize(self) -> None:
        if await self.dst.is_empty():
            objs = await self.src.get_all()
            await self.dst.insert(objs)
            await self.commit()

    async def commit(self) -> None:
        await self.dst.commit()
