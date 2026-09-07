from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import SimpleReplaceDB
from app.infrastructure.db.dao.local.base import Model
from app.infrastructure.db.dao.local.main_table import MainTableDAO


class SimpleReplaceDAO(MainTableDAO[Model, SimpleReplaceDB]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        super().__init__(model, SimpleReplaceDB, session)

    async def refresh(self, objs: list[SimpleReplaceDB]) -> None:
        await self._upsert_by_matching(objs, fields=["group"])

    async def reload(self, objs: list[SimpleReplaceDB]) -> None:
        await self.delete_all()
        await self.insert(objs)
