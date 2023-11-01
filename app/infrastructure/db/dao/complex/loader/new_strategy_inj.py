from dataclasses import dataclass

from app.infrastructure.db.dao import excel, local
from app.infrastructure.db.dao.complex.loader.excel_loader import ExcelLoader


@dataclass
class NewStrategyInjLoader(
    ExcelLoader[excel.NewStrategyInjDAO, local.NewStrategyInjDAO]
):
    pass
