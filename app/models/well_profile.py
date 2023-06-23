from typing import Optional

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

# from app.core.config import settings
from app.core.local_db import Base
from app.models import types
from app.models.mixins import date_stamp_factory


DateStampMixin = date_stamp_factory('rec_date')


class WellProfile(DateStampMixin, Base):
    field: Mapped[types.field_type]
    well_name: Mapped[types.well_type]
    cid_all: Mapped[types.multi_reservoir_type]
    cid_layer: Mapped[Optional[types.reservoir_type]]
    layer: Mapped[Optional[types.multi_layer_type]]

    uwi: Mapped[str] = mapped_column(String(10))
    well_type: Mapped[Optional[str]]
    top: Mapped[float]
    bottom: Mapped[float]
    abstop: Mapped[Optional[float]]
    absbotm: Mapped[Optional[float]]
    diff_absorp: Mapped[Optional[float]]
    tot_absorp: Mapped[Optional[float]]
    liq_rate: Mapped[Optional[float]]
    remarks: Mapped[Optional[str]]

    __table_args__ = (
        Index('uwi-rec_date', 'uwi', 'rec_date'),
    )
