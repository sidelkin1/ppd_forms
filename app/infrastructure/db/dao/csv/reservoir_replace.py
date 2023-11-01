from pathlib import Path

from app.core.models.dto import RegexReplaceDB
from app.infrastructure.db.dao.csv.base import BaseDAO


class ReservoirReplaceDAO(BaseDAO[RegexReplaceDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(RegexReplaceDB, filepath)
