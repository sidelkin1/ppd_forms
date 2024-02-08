from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import MonthlyReportDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import MonthlyReport


class MonthlyReportDAO(MainTableDAO[MonthlyReport, MonthlyReportDB]):
    constraint_name: str = "uq__monthlyreport__field"
    excluded_fields: list[str] = [
        "cid_all",
        "oil_v",
        "water_v",
        "water",
        "days",
        "cum_oil_v",
        "cum_water_v",
        "cum_water",
        "oil_fvf",
    ]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MonthlyReport, MonthlyReportDB, session)

    async def reload(self, objs: list[MonthlyReportDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[MonthlyReportDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
