from sqlalchemy.orm import Session

from app.core.models.dto import ReservoirListDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import select_reservoirs


class ReservoirListDAO(BaseDAO[ReservoirListDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(ReservoirListDB, select_reservoirs(), session)
