from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

# from app.core.config import settings
from app.core.local_db import Base
from app.models import types
from app.models.mixins import date_stamp_factory


DateStampMixin = date_stamp_factory('dat_rep')


class MonthlyReport(DateStampMixin, Base):
    field: Mapped[types.field_type]
    well_name: Mapped[types.well_type]
    cid_all: Mapped[types.multi_reservoir_type]
    cid: Mapped[types.reservoir_type]

    oil_v: Mapped[float]
    water_v: Mapped[float]
    water: Mapped[float]
    days: Mapped[float]

    @hybrid_property
    def liquid(self):
        return self.oil_v + self.water_v

    @hybrid_property
    def liq_rate(self):
        return self.liquid / self.days

    @hybrid_property
    def inj_rate(self):
        return self.water / self.days

    __table_args__ = (
        UniqueConstraint(
            'field', 'well_name', 'cid', 'dat_rep',
            name='field-well_name-cid-dat_rep',
        ),
    )
