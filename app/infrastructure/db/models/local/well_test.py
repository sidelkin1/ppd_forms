from datetime import date

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.infrastructure.db import types
from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory


class WellTest(date_stamp_factory("end_date"), Base):
    field: Mapped[types.field_type]
    well: Mapped[types.well_type]
    reservoir: Mapped[types.multi_split_reservoir_type]
    well_type: Mapped[str | None]
    well_test: Mapped[str]
    start_date: Mapped[date]
    end_date: Mapped[date]
    resp_owc: Mapped[float | None]
    oil_perm: Mapped[float | None]
    wat_perm: Mapped[float | None]
    liq_perm: Mapped[float | None]
    skin_factor: Mapped[float | None]
    prod_index: Mapped[float | None]
    frac_length: Mapped[float | None]
    reliability: Mapped[str | None]

    __table_args__ = (
        UniqueConstraint(
            "field", "well", "reservoir", "well_test", "end_date"
        ),
        Index(None, "field"),
        Index(None, "well"),
        Index(None, "reservoir"),
        Index(None, "end_date"),
    )
