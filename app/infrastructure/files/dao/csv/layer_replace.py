from pathlib import Path

from app.core.models.dto import SimpleReplaceDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class LayerReplaceDAO(BaseDAO[SimpleReplaceDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(SimpleReplaceDB, filepath)
