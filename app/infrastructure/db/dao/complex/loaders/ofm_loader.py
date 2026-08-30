from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.dao.complex.loaders.base import (
    BaseLoader,
    DestinationDAO,
)
from app.infrastructure.db.dao.complex.loaders.factory import (
    LoaderFactory,
    loader_factory,
)
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO

SourceDAO = TypeVar(
    "SourceDAO", bound=BaseDAO, covariant=True, contravariant=False
)
LoaderT = TypeVar("LoaderT", bound="OfmLoader")


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


OfmLoaderFactory = LoaderFactory[Session, LoaderT]


def ofm_loader_factory(
    loader_cls: type[LoaderT],
    ofm_dao: Callable[[Session], SourceDAO],
    local_dao: Callable[[AsyncSession], DestinationDAO],
) -> OfmLoaderFactory[LoaderT]:
    """Фабрика лоадеров с источником в OFM (Oracle)."""
    return loader_factory(loader_cls, ofm_dao, local_dao)
