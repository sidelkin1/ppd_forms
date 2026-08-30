from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.excel_loader import (
    ExcelLoader,
    ExcelLoaderFactory,
    excel_loader_factory,
)
from app.infrastructure.files.dao import excel


@dataclass
class InjWellDatabaseLoader(
    ExcelLoader[excel.InjWellDatabaseDAO, local.InjWellDatabaseDAO]
):
    pass


inj_well_database_loader: ExcelLoaderFactory[InjWellDatabaseLoader] = (
    excel_loader_factory(
        InjWellDatabaseLoader,
        excel.InjWellDatabaseDAO,
        local.InjWellDatabaseDAO,
    )
)
