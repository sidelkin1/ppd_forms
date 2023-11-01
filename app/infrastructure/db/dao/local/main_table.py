from datetime import date

from sqlalchemy import delete, func, select, tuple_
from sqlalchemy.dialects.postgresql import insert as upsert

from app.infrastructure.db.dao.local.base import BaseDAO, DataModel, Model


class MainTableDAO(BaseDAO[Model, DataModel]):
    async def _upsert_by_matching(
        self, objs: list[DataModel], fields: list[str]
    ) -> None:
        await self.session.execute(
            delete(self.model).where(
                tuple_(*(getattr(self.model, field) for field in fields)).in_(
                    [
                        tuple(
                            data[field]
                            for field in fields
                            if (data := dto.model_dump())
                        )
                        for dto in objs
                    ]
                )
            )
        )
        await self.insert(objs)

    async def _upsert_by_constraint(
        self, objs: list[DataModel], constraint: str, fields: list[str]
    ) -> None:
        stmt = upsert(self.model)
        await self.session.execute(
            stmt.on_conflict_do_update(
                constraint=constraint,
                set_={
                    field: getattr(stmt.excluded, field) for field in fields
                },
            )
            if fields
            else stmt.on_conflict_do_nothing(constraint=constraint),
            [dto.model_dump() for dto in objs],
        )

    async def refresh(self, objs: list[DataModel]) -> None:
        raise NotImplementedError

    async def reload(self, objs: list[DataModel]) -> None:
        raise NotImplementedError

    async def date_range(self) -> tuple[date, date]:
        result = await self.session.execute(
            select(
                func.min(self.model.date_stamp),
                func.max(self.model.date_stamp),
            )
        )
        return result.one()
