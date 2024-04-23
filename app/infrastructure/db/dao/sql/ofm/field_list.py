from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models.dto import UneftFieldDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import (
    select_field,
    select_fields,
    select_injection_field,
    select_injection_fields,
    select_production_field,
    select_production_fields,
)


class FieldListDAO(BaseDAO[UneftFieldDB]):
    def __init__(self, session: Session) -> None:
        self.querysets = {
            "fields": select_fields(),
            "production_fields": select_production_fields(),
            "injection_fields": select_injection_fields(),
            "field": select_field(),
            "production_field": select_production_field(),
            "injection_field": select_injection_field(),
        }
        super().__init__(UneftFieldDB, select(), session)

    async def get_fields(self) -> list[UneftFieldDB]:
        self.queryset = self.querysets["fields"]
        return await self.get_by_params()

    async def get_production_fields(self) -> list[UneftFieldDB]:
        self.queryset = self.querysets["production_fields"]
        return await self.get_by_params()

    async def get_injection_fields(self) -> list[UneftFieldDB]:
        self.queryset = self.querysets["injection_fields"]
        return await self.get_by_params()

    async def get_field(self, field_id: int) -> UneftFieldDB | None:
        self.queryset = self.querysets["field"]
        fields = await self.get_by_params(field_id=field_id)
        return fields[0] if fields else None

    async def get_production_field(self, field_id: int) -> UneftFieldDB | None:
        self.queryset = self.querysets["production_field"]
        fields = await self.get_by_params(field_id=field_id)
        return fields[0] if fields else None

    async def get_injection_field(self, field_id: int) -> UneftFieldDB | None:
        self.queryset = self.querysets["injection_field"]
        fields = await self.get_by_params(field_id=field_id)
        return fields[0] if fields else None
