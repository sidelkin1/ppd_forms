from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import InjWellDatabaseDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import InjWellDatabase


class InjWellDatabaseDAO(MainTableDAO[InjWellDatabase, InjWellDatabaseDB]):
    constraint_name: str = "uq__injwelldatabase__field"
    excluded_fields: list[str] = ["created_at"]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(InjWellDatabase, InjWellDatabaseDB, session)

    async def reload(self, objs: list[InjWellDatabaseDB]) -> None:
        await self.delete_all()
        await self.insert(objs)

    async def refresh(self, objs: list[InjWellDatabaseDB]) -> None:
        await self._upsert_by_constraint(
            objs, self.constraint_name, self.excluded_fields
        )
