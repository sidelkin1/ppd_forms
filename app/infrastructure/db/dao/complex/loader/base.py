from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from app.infrastructure.db.dao import local

SourceDAO = TypeVar(
    "SourceDAO", bound=Any, covariant=True, contravariant=False
)
DestinationDAO = TypeVar(
    "DestinationDAO",
    bound=local.MainTableDAO,
    covariant=True,
    contravariant=False,
)


@dataclass
class BaseLoader(Generic[SourceDAO, DestinationDAO]):
    src: SourceDAO
    dst: DestinationDAO

    async def refresh(self) -> None:
        raise NotImplementedError

    async def reload(self) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        await self.dst.commit()
