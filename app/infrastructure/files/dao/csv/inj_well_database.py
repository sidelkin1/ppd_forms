from pathlib import Path

from app.core.models.dto import InjWellDatabaseDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class InjWellDatabaseDAO(BaseDAO[InjWellDatabaseDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(InjWellDatabaseDB, filepath)
