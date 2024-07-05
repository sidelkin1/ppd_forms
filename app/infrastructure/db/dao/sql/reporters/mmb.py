from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    select_tank_alternative_rates,
    select_tank_bhp,
    select_tank_pressures,
    select_tank_rates,
    select_tank_works,
)


class MmbReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_tank_rates(),
                "resp": select_tank_pressures(),
                "bhp": select_tank_bhp(),
                "works": select_tank_works(),
            },
            pool,
        )


class MmbAltReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_tank_alternative_rates(),
                "resp": select_tank_pressures(),
                "bhp": select_tank_bhp(),
                "works": select_tank_works(),
            },
            pool,
        )
