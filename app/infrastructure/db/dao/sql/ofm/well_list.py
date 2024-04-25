from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.dto import UneftWellDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import (
    select_injection_wells,
    select_production_wells,
)


class WellListDAO(BaseDAO[UneftWellDB]):
    def __init__(self, session: Session) -> None:
        self.querysets = {
            "production": select_production_wells(),
            "injection": select_injection_wells(),
        }
        super().__init__(UneftWellDB, select(), session)

    async def get_production_wells(self, field_id: int) -> list[UneftWellDB]:
        self.queryset = self.querysets["production"]
        return await self.get_by_params(field_id=field_id)

    async def get_injection_wells(self, field_id: int) -> list[UneftWellDB]:
        self.queryset = self.querysets["injection"]
        return await self.get_by_params(field_id=field_id)
