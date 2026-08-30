from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import (
    ExcelLoader,
    ExcelLoaderFactory,
    excel_loader_factory,
)
from app.infrastructure.files.dao import excel


@dataclass
class NewStrategyOilLoader(
    ExcelLoader[excel.NewStrategyOilDAO, local.NewStrategyOilDAO]
):
    pass


new_strategy_oil_loader: ExcelLoaderFactory[NewStrategyOilLoader] = (
    excel_loader_factory(
        NewStrategyOilLoader,
        excel.NewStrategyOilDAO,
        local.NewStrategyOilDAO,
    )
)
