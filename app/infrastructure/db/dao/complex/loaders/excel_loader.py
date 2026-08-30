from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dao.complex.loaders.base import (
    BaseLoader,
    DestinationDAO,
)
from app.infrastructure.db.dao.complex.loaders.factory import (
    LoaderFactory,
    loader_factory,
)
from app.infrastructure.files.dao.excel.base import AbstractBaseDAO

SourceDAO = TypeVar(
    "SourceDAO", bound=AbstractBaseDAO, covariant=True, contravariant=False
)
LoaderT = TypeVar("LoaderT", bound="ExcelLoader")


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


ExcelLoaderFactory = LoaderFactory[Path, LoaderT]


def excel_loader_factory(
    loader_cls: type[LoaderT],
    excel_dao: Callable[[Path], SourceDAO],
    local_dao: Callable[[AsyncSession], DestinationDAO],
) -> ExcelLoaderFactory[LoaderT]:
    """Фабрика лоадеров с источником в Excel-файле."""
    return loader_factory(loader_cls, excel_dao, local_dao)
