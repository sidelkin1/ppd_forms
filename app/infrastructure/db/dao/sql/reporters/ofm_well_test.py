from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import well_test


class OfmWellTestReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__({"neighbs": well_test.select_ofm_neighbs()}, pool)
