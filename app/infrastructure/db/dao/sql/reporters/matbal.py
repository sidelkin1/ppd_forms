from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    select_field_resp,
    select_field_sum_alternative_rates,
    select_field_sum_rates,
    select_well_resp,
    select_well_sum_alternative_rates,
    select_well_sum_rates,
)


class FieldMatbalReporter(OfmBaseDAO):
    """MER rates for the whole field and its pressure measurements."""

    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_field_sum_rates(),
                "resp": select_field_resp(),
            },
            pool,
        )


class AltFieldMatbalReporter(OfmBaseDAO):
    """FieldMatbalReporter on the alternative MER source."""

    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_field_sum_alternative_rates(),
                "resp": select_field_resp(),
            },
            pool,
        )


class WellMatbalReporter(OfmBaseDAO):
    """MER rates for the given wells and their pressure measurements."""

    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_well_sum_rates(),
                "resp": select_well_resp(),
            },
            pool,
        )


class AltWellMatbalReporter(OfmBaseDAO):
    """WellMatbalReporter on the alternative MER source."""

    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "rates": select_well_sum_alternative_rates(),
                "resp": select_well_resp(),
            },
            pool,
        )
