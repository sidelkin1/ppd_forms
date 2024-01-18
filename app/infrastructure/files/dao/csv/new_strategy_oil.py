from pathlib import Path

from app.core.models.dto import NewStrategyOilDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class NewStrategyOilDAO(BaseDAO[NewStrategyOilDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(NewStrategyOilDB, filepath)
