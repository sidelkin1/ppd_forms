"""Обобщённая фабрика лоадеров.

Собирает лоадер из пары DAO (источник -> local) по переданным классам,
чтобы не дублировать конструкцию в крон-задачах и обработчиках.
Фабрика обобщена по типу контекста источника: для OFM это
`Session`, для Excel — `Path`.
"""

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dao.complex.loaders.base import (
    BaseLoader,
    DestinationDAO,
)

Loader = TypeVar("Loader", bound=BaseLoader)
Source = TypeVar("Source")
SourceDAO = TypeVar("SourceDAO")

LoaderFactory = Callable[[AsyncSession, Source], Loader]


def loader_factory(
    loader_cls: type[Loader],
    src_dao: Callable[[Source], SourceDAO],
    dst_dao: Callable[[AsyncSession], DestinationDAO],
) -> LoaderFactory[Source, Loader]:
    """Карри-фабрика: классы один раз — дальше только контексты."""

    def factory(local_session: AsyncSession, source: Source) -> Loader:
        return loader_cls(
            src=src_dao(source),
            dst=dst_dao(local_session),
        )

    return factory
