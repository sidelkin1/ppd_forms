from dataclasses import dataclass

from app.infrastructure.db.dao import excel, local
from app.infrastructure.db.dao.complex.loader.excel_loader import ExcelLoader


@dataclass
class NewStrategyOilLoader(
    ExcelLoader[excel.NewStrategyOilDAO, local.NewStrategyOilDAO]
):
    pass
