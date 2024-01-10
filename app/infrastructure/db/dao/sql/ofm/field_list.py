from sqlalchemy.orm import Session

from app.core.models.dto import FieldListDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import select_fields


class FieldListDAO(BaseDAO[FieldListDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(FieldListDB, select_fields(), session)
