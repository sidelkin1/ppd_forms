from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import ExcelLoader
from app.infrastructure.files.dao import excel


@dataclass
class NewStrategyOilLoader(
    ExcelLoader[excel.NewStrategyOilDAO, local.NewStrategyOilDAO]
):
    pass
