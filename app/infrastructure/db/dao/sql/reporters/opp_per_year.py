from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    select_well_profiles,
)


class OppPerYearReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__({"profile": select_well_profiles()}, pool)
