from pathlib import Path

from app.core.models.dto import WellTestDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class WellTestDAO(BaseDAO[WellTestDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(WellTestDB, filepath)
