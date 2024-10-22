from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import mmb


class MmbReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": mmb.select_tank_rates(),
                "resp": mmb.select_tank_pressures(),
                "bhp": mmb.select_tank_bhp(),
                "works": mmb.select_tank_works(),
            },
            pool,
        )


class MmbAltReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": mmb.select_tank_alternative_rates(),
                "resp": mmb.select_tank_pressures(),
                "bhp": mmb.select_tank_bhp(),
                "works": mmb.select_tank_works(),
            },
            pool,
        )
