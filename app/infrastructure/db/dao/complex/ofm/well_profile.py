from sqlalchemy.orm import Session

from app.core.models.dto import WellProfileDB
from app.infrastructure.db.dao.complex.ofm.base import BaseDAO
from app.infrastructure.db.dao.complex.ofm.querysets.well_profile import (
    select_well_profiles,
)


class WellProfileDAO(BaseDAO[WellProfileDB]):
    def __init__(self, session: Session) -> None:
        super().__init__(WellProfileDB, select_well_profiles(), session)
