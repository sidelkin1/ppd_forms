from sqlalchemy.orm import Session

from app.core.models.dto import UneftFieldDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import select_fields


class FieldListDAO(BaseDAO[UneftFieldDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(UneftFieldDB, select_fields(), session)
