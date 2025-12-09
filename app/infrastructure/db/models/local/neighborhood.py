from datetime import date

from sqlalchemy import Index, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db import types
from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory


class Neighborhood(date_stamp_factory("created_at"), Base):
    field: Mapped[types.field_type]
    reservoir: Mapped[types.reservoir_type]
    well: Mapped[types.well_no_branch_type]
    neighbs: Mapped[types.multi_well_no_branch_type]
    created_at: Mapped[date] = mapped_column(
        server_default=text("current_date")
    )

    __table_args__ = (
        UniqueConstraint("field", "reservoir", "well"),
        Index(None, "field"),
        Index(None, "well"),
        Index(None, "reservoir"),
    )
