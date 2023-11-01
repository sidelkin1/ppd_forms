from datetime import date

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory
from app.infrastructure.db.types import types


class NewStrategyInj(date_stamp_factory("gtm_date"), Base):
    field: Mapped[types.field_type]
    well: Mapped[types.well_type]
    reservoir: Mapped[types.multi_split_reservoir_type]
    gtm_date: Mapped[date]
    gtm_description: Mapped[str]
    oil_recovery: Mapped[float | None]
    effect_end: Mapped[date | None]
    gtm_group: Mapped[str | None]
    oil_rate: Mapped[float | None]
    gtm_problem: Mapped[str]
    reservoir_neighbs: Mapped[types.multi_split_reservoir_type | None]
    neighbs: Mapped[types.multi_well_type | None]

    __table_args__ = (
        UniqueConstraint("field", "well", "gtm_date"),
        Index(None, "field"),
        Index(None, "well"),
        Index(None, "gtm_date"),
    )
