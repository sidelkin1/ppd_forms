from pathlib import Path

from app.core.models.dto import NeighborhoodDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class NeighborhoodDAO(BaseDAO[NeighborhoodDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(NeighborhoodDB, filepath)
