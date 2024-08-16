from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.models.dto import UneftReservoirDB
from app.infrastructure.db.dao.sql.ofm.asset_list import AssetListDAO
from app.infrastructure.db.dao.sql.ofm.querysets import select_reservoirs


class ReservoirListDAO(AssetListDAO[UneftReservoirDB]):
    def __init__(self, session: Session, redis: Redis) -> None:
        super().__init__(
            UneftReservoirDB,
            {"reservoirs": select_reservoirs()},
            ["fields:{}:reservoirs"],
            session,
            redis,
        )

    async def get_reservoirs(self, field_id: int) -> list[UneftReservoirDB]:
        return await self.get_by_field("reservoirs", field_id)
