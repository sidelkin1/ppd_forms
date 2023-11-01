from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import WellProfileDB
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.models.local import WellProfile


class WellProfileDAO(MainTableDAO[WellProfile, WellProfileDB]):
    matching_fields: list[str] = ["uwi", "rec_date"]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WellProfile, WellProfileDB, session)

    async def refresh(self, objs: list[WellProfileDB]) -> None:
        await self._upsert_by_matching(objs, self.matching_fields)
