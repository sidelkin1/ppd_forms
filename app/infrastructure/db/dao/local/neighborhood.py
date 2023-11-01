from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import NeighborhoodDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import Neighborhood


class NeighborhoodDAO(MainTableDAO[Neighborhood, NeighborhoodDB]):
    constraint_name: str = "uq__neighborhood__field"
    excluded_fields: list[str] = ["neighbs", "created_at"]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Neighborhood, NeighborhoodDB, session)

    async def reload(self, objs: list[NeighborhoodDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[NeighborhoodDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
