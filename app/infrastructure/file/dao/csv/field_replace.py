from pathlib import Path

from app.core.models.dto import RegexReplaceDB
from app.infrastructure.file.dao.csv.base import BaseDAO


class FieldReplaceDAO(BaseDAO[RegexReplaceDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(RegexReplaceDB, filepath)
