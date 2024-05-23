from sqlalchemy.orm import Session

from app.core.models.dto import UneftReservoirDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import select_reservoirs


class ReservoirListDAO(BaseDAO[UneftReservoirDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(UneftReservoirDB, select_reservoirs(), session)

    async def get_reservoirs(self, field_id: int) -> list[UneftReservoirDB]:
        return await self.get_by_params(field_id=field_id)
