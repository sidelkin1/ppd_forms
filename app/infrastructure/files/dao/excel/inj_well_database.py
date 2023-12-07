from pathlib import Path

from app.core.models.dto import InjWellDatabaseDB
from app.infrastructure.files.dao.excel.base import BaseDAO
from app.infrastructure.files.dao.excel.configs.inj_well_database import (
    column_names,
    excel_options,
)


class InjWellDatabaseDAO(BaseDAO[InjWellDatabaseDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(
            InjWellDatabaseDB, filepath, excel_options, column_names
        )
