from datetime import date

from sqlalchemy import (
    ColumnElement,
    Float,
    Index,
    UniqueConstraint,
    cast,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory
from app.infrastructure.db.types import types


class MonthlyReport(date_stamp_factory("dat_rep"), Base):
    field: Mapped[types.field_type]
    well_name: Mapped[types.well_type]
    cid_all: Mapped[types.multi_reservoir_type]
    cid: Mapped[types.reservoir_type]
    dat_rep: Mapped[date]
    oil: Mapped[float]
    oil_v: Mapped[float]
    water_v: Mapped[float]
    water: Mapped[float]
    days: Mapped[float]

    @hybrid_property
    def liquid(self) -> float:
        return self.oil_v + self.water_v

    @hybrid_property
    def oil_rate(self) -> float:
        return self.oil / self.days

    @hybrid_property
    def liq_rate(self) -> float:
        return self.liquid / self.days

    @hybrid_property
    def inj_rate(self) -> float:
        return self.water / self.days

    @hybrid_property
    def watercut(self) -> float:
        return self.liquid and self.water_v / self.liquid

    @watercut.inplace.expression
    @classmethod
    def _watercut_expression(cls) -> ColumnElement[Float]:
        return func.coalesce(
            cls.water_v / func.nullif(cls.liquid, 0), cast(0, Float)
        ).label("watercut")

    __table_args__ = (
        UniqueConstraint("field", "well_name", "cid", "dat_rep"),
        Index(None, "field"),
        Index(None, "well_name"),
        Index(None, "cid"),
        Index(None, "dat_rep"),
        Index(None, "cid_all"),
    )
