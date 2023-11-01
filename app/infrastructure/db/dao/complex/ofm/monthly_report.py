from sqlalchemy.orm import Session

from app.core.models.dto import MonthlyReportDB
from app.infrastructure.db.dao.complex.ofm.base import BaseDAO
from app.infrastructure.db.dao.complex.ofm.querysets.monthly_report import (
    select_well_rates,
)


class MonthlyReportDAO(BaseDAO[MonthlyReportDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(MonthlyReportDB, select_well_rates(), session)
