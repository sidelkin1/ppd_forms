from pathlib import Path

from app.core.models.dto import MonthlyReportDB
from app.infrastructure.db.dao.csv.base import BaseDAO


class MonthlyReportDAO(BaseDAO[MonthlyReportDB]):
    def __init__(self, filepath: Path) -> None:
        super().__init__(MonthlyReportDB, filepath)
