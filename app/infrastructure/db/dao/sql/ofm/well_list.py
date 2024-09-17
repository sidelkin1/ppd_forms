from datetime import timedelta

from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.models.dto import UneftWellDB
from app.infrastructure.db.dao.sql.ofm.asset_list import AssetListDAO
from app.infrastructure.db.dao.sql.ofm.querysets import (
    select_injection_wells,
    select_production_wells,
)


class WellListDAO(AssetListDAO[UneftWellDB]):
    def __init__(
        self, session: Session, redis: Redis, expires: timedelta
    ) -> None:
        super().__init__(
            UneftWellDB,
            {
                "production_wells": select_production_wells(),
                "injection_wells": select_injection_wells(),
            },
            ["fields:{}:wells:production", "fields:{}:wells:injection"],
            session,
            redis,
            expires,
        )

    async def get_production_wells(self, field_id: int) -> list[UneftWellDB]:
        return await self.get_by_field("production_wells", field_id)

    async def get_injection_wells(self, field_id: int) -> list[UneftWellDB]:
        return await self.get_by_field("injection_wells", field_id)
