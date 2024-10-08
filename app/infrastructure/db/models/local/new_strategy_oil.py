from datetime import date

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.infrastructure.db import types
from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory


class NewStrategyOil(date_stamp_factory("vnr_date"), Base):
    field: Mapped[types.field_type]
    well: Mapped[types.well_type]
    reservoir_before: Mapped[types.multi_split_reservoir_type]
    reservoir_after: Mapped[types.multi_split_reservoir_type]
    vnr_date: Mapped[date]
    gtm_name: Mapped[types.gtm_type]
    start_date: Mapped[date]

    __table_args__ = (
        UniqueConstraint("field", "well", "vnr_date"),
        Index(None, "field"),
        Index(None, "well"),
        Index(None, "vnr_date"),
    )
