from pathlib import Path

from app.core.models.dto import WellProfileDB
from app.infrastructure.file.dao.csv.base import BaseDAO


class WellProfileDAO(BaseDAO[WellProfileDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(WellProfileDB, filepath)
