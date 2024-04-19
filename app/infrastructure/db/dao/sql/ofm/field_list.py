from sqlalchemy.orm import Session

from app.core.models.dto import UneftFieldDB
from app.infrastructure.db.dao.sql.ofm.base import BaseDAO
from app.infrastructure.db.dao.sql.ofm.querysets import (
    select_fields,
    select_injection_fields,
    select_production_fields,
)


class FieldListDAO(BaseDAO[UneftFieldDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(UneftFieldDB, select_fields(), session)


class ProductionFieldListDAO(BaseDAO[UneftFieldDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(UneftFieldDB, select_production_fields(), session)


class InjectionFieldListDAO(BaseDAO[UneftFieldDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(UneftFieldDB, select_injection_fields(), session)
