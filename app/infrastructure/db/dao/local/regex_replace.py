from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.dto import RegexReplaceDB
from app.infrastructure.db.dao.local.base import Model
from app.infrastructure.db.dao.local.main_table import MainTableDAO
from app.infrastructure.db.mappers import BaseMapper


class RegexReplaceDAO(MainTableDAO[Model, RegexReplaceDB]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        super().__init__(model, RegexReplaceDB, session)

    async def get_grouped_patterns(self) -> list[RegexReplaceDB]:
        subq = (
            select(
                func.min(self.model.id).label("id"),
                self.model.group,
                func.string_agg(self.model.pattern, "|").label("pattern"),
                self.model.replace,
                func.coalesce(self.model.order, BaseMapper.NULL_ORDER).label(
                    "order"
                ),
            )
            .group_by(self.model.group, self.model.replace, self.model.order)
            .subquery()
        )
        result = await self.session.execute(
            select(
                subq.c.group, subq.c.pattern, subq.c.replace, subq.c.order
            ).order_by(subq.c.id)
        )
        return [self.data_model(**row._mapping) for row in result.all()]

    async def refresh(self, objs: list[RegexReplaceDB]) -> None:
        await self._upsert_by_matching(objs, fields=["group"])

    async def reload(self, objs: list[RegexReplaceDB]) -> None:
        await self.delete_all()
        await self.insert(objs)
