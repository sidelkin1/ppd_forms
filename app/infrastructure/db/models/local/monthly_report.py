from datetime import date

from sqlalchemy import Float, Index, Label, UniqueConstraint, cast, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

from app.infrastructure.db import types
from app.infrastructure.db.models.local.base import Base
from app.infrastructure.db.models.local.mixins import date_stamp_factory

FVF_DEFAULT_VALUE: float = 1


class MonthlyReport(date_stamp_factory("dat_rep"), Base):
    field: Mapped[types.ofm_field_type]
    well_name: Mapped[types.ofm_well_type]
    cid_all: Mapped[types.multi_reservoir_type]
    cid: Mapped[types.ofm_reservoir_type]
    dat_rep: Mapped[date]
    oil: Mapped[float]
    oil_v: Mapped[float]
    water_v: Mapped[float]
    water: Mapped[float]
    days: Mapped[float]
    cum_oil_v: Mapped[float]
    cum_water_v: Mapped[float]
    cum_water: Mapped[float]
    oil_fvf: Mapped[float | None]

    @hybrid_property
    def oil_fvf_or_default(self) -> float:
        return FVF_DEFAULT_VALUE if self.oil_fvf is None else self.oil_fvf

    @oil_fvf_or_default.inplace.expression
    @classmethod
    def _oil_fvf_or_default_expression(cls) -> Label[float]:
        return func.coalesce(  # type: ignore
            cls.oil_fvf, cast(FVF_DEFAULT_VALUE, Float)
        ).label("_oil_fvf")

    @hybrid_property
    def liquid(self) -> float:
        return self.oil_v + self.water_v

    @hybrid_property
    def liquid_res(self) -> float:
        return self.oil_v * self.oil_fvf_or_default + self.water_v

    @hybrid_property
    def cum_liquid(self) -> float:
        return self.cum_oil_v + self.cum_water_v

    @hybrid_property
    def cum_liquid_res(self) -> float:
        return self.cum_oil_v * self.oil_fvf_or_default + self.cum_water_v

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
    def _watercut_expression(cls) -> Label[float]:
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
