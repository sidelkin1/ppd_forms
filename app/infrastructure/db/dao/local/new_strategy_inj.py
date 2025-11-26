from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import NewStrategyInjDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import NewStrategyInj


class NewStrategyInjDAO(MainTableDAO[NewStrategyInj, NewStrategyInjDB]):
    constraint_name: str = "uq__newstrategyinj__field"
    excluded_fields: list[str] = [
        "gtm_description",
        "oil_recovery",
        "effect_end",
        "gtm_group",
        "oil_rate",
        "gtm_problem",
        "reservoir_neighbs",
        "neighbs",
    ]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(NewStrategyInj, NewStrategyInjDB, session)

    async def reload(self, objs: list[NewStrategyInjDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[NewStrategyInjDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
