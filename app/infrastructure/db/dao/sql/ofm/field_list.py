from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.models.dto import UneftFieldDB
from app.infrastructure.db.dao.sql.ofm.asset_list import AssetListDAO
from app.infrastructure.db.dao.sql.ofm.querysets import (
    select_fields,
    select_injection_fields,
    select_production_fields,
)


class FieldListDAO(AssetListDAO[UneftFieldDB]):
    def __init__(self, session: Session, redis: Redis) -> None:
        super().__init__(
            UneftFieldDB,
            {
                "fields": select_fields(),
                "production_fields": select_production_fields(),
                "injection_fields": select_injection_fields(),
                "field": select_fields(with_field_id=True),
                "production_field": select_fields(with_field_id=True),
                "injection_field": select_fields(with_field_id=True),
            },
            [
                "fields",
                "fields:production",
                "fields:injection",
                "fields:{}",
                "fields:{}:production",
                "fields:{}:injection",
            ],
            session,
            redis,
        )

    async def get_fields(self) -> list[UneftFieldDB]:
        return await self.get_all("fields")

    async def get_production_fields(self) -> list[UneftFieldDB]:
        return await self.get_all("production_fields")

    async def get_injection_fields(self) -> list[UneftFieldDB]:
        return await self.get_all("injection_fields")

    async def get_field(self, field_id: int) -> UneftFieldDB | None:
        fields = await self.get_by_field("field", field_id)
        return fields[0] if fields else None

    async def get_production_field(self, field_id: int) -> UneftFieldDB | None:
        fields = await self.get_by_field("production_field", field_id)
        return fields[0] if fields else None

    async def get_injection_field(self, field_id: int) -> UneftFieldDB | None:
        fields = await self.get_by_field("injection_field", field_id)
        return fields[0] if fields else None
