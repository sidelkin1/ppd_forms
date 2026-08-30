from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import (
    ExcelLoader,
    ExcelLoaderFactory,
    excel_loader_factory,
)
from app.infrastructure.files.dao import excel


@dataclass
class NeighborhoodLoader(
    ExcelLoader[excel.NeighborhoodDAO, local.NeighborhoodDAO]
):
    pass


neighborhood_loader: ExcelLoaderFactory[NeighborhoodLoader] = (
    excel_loader_factory(
        NeighborhoodLoader, excel.NeighborhoodDAO, local.NeighborhoodDAO
    )
)
