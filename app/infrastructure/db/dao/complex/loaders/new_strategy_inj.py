from dataclasses import dataclass
from functools import partial

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import (
    ExcelLoader,
    ExcelLoaderFactory,
    excel_loader_factory,
)
from app.infrastructure.files.dao import excel


@dataclass
class NewStrategyInjLoader(
    ExcelLoader[excel.NewStrategyInjDAO, local.NewStrategyInjDAO]
):
    pass


def new_strategy_inj_loader(
    delimiter: str,
) -> ExcelLoaderFactory[NewStrategyInjLoader]:
    """Фабрика МСИ: разделитель известен только из настроек в рантайме."""
    return excel_loader_factory(
        NewStrategyInjLoader,
        partial(excel.NewStrategyInjDAO, delimiter=delimiter),
        local.NewStrategyInjDAO,
    )
