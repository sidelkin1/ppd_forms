from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import WellTestDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import WellTest


class WellTestDAO(MainTableDAO[WellTest, WellTestDB]):
    constraint_name: str = "uq__welltest__field"
    excluded_fields: list[str] = [
        "layer",
        "well_type",
        "start_date",
        "oil_perm",
        "wat_perm",
        "liq_perm",
        "skin_factor",
        "resp_owc",
        "prod_index",
        "frac_length",
        "reliability",
    ]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WellTest, WellTestDB, session)

    async def reload(self, objs: list[WellTestDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[WellTestDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
