from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import well_test

PERF_COLUMNS = (
    "field",
    "well",
    "reservoir",
    "branch",
    "comp_date",
    "close_date",
)


class OfmWellTestReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "branches": well_test.select_well_branch(),
                "perfs": well_test.select_well_perfs(),
                "neighbs": well_test.select_ofm_neighbs(),
                "pvt": well_test.select_pvt_props(),
            },
            pool,
        )
