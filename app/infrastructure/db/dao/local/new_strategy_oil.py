from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import NewStrategyOilDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import NewStrategyOil


class NewStrategyOilDAO(MainTableDAO[NewStrategyOil, NewStrategyOilDB]):
    constraint_name: str = "uq__newstrategyoil__field"
    excluded_fields: list[str] = [
        "reservoir_before",
        "reservoir_after",
        "gtm_name",
        "start_date",
    ]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(NewStrategyOil, NewStrategyOilDB, session)

    async def reload(self, objs: list[NewStrategyOilDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[NewStrategyOilDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
