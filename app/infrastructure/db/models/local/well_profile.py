from datetime import date

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory
from app.infrastructure.db.types import types


class WellProfile(date_stamp_factory("rec_date"), Base):
    field: Mapped[types.field_type]
    well_name: Mapped[types.well_type]
    cid_all: Mapped[types.multi_reservoir_type]
    cid_layer: Mapped[types.reservoir_type | None]
    layer: Mapped[types.multi_layer_type | None]
    rec_date: Mapped[date]
    uwi: Mapped[str] = mapped_column(String(10))
    well_type: Mapped[str | None]
    top: Mapped[float]
    bottom: Mapped[float]
    abstop: Mapped[float | None]
    absbotm: Mapped[float | None]
    diff_absorp: Mapped[float | None]
    tot_absorp: Mapped[float | None]
    liq_rate: Mapped[float | None]
    remarks: Mapped[str | None]

    __table_args__ = (
        Index(None, "uwi", "rec_date"),
        Index(None, "field"),
        Index(None, "well_name"),
        Index(None, "uwi"),
        Index(None, "rec_date"),
        Index(None, "cid_all"),
    )
