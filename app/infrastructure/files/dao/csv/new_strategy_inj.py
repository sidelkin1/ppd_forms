from pathlib import Path

from app.core.models.dto import NewStrategyInjDB
from app.infrastructure.files.dao.csv.base import BaseDAO


class NewStrategyInjDAO(BaseDAO[NewStrategyInjDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(NewStrategyInjDB, filepath)
