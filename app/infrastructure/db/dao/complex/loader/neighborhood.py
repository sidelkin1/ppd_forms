from dataclasses import dataclass

from app.infrastructure.db.dao import excel, local
from app.infrastructure.db.dao.complex.loader.excel_loader import ExcelLoader


@dataclass
class NeighborhoodLoader(
    ExcelLoader[excel.NeighborhoodDAO, local.NeighborhoodDAO]
):
    pass
