from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import (
    ExcelLoader,
    ExcelLoaderFactory,
    excel_loader_factory,
)
from app.infrastructure.files.dao import excel


@dataclass
class WellTestLoader(ExcelLoader[excel.WellTestDAO, local.WellTestDAO]):
    pass


well_test_loader: ExcelLoaderFactory[WellTestLoader] = excel_loader_factory(
    WellTestLoader, excel.WellTestDAO, local.WellTestDAO
)
