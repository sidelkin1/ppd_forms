from enum import Enum

from sqlalchemy import Date, bindparam, func, literal_column, select, union
from sqlalchemy.sql.expression import ColumnClause, Label, Select, Subquery

from app.infrastructure.db.dao.sql.querysets.common import (
    select_cids,
    select_description,
    select_well_name,
)
from app.infrastructure.db.models.ofm.base import Base
from app.infrastructure.db.models.ofm.reflected import (
    HeaderId,
    MonthlyInj,
    MonthlyProd,
    Reservoir,
    WellStockHistExt,
)


class WellMode(Enum):
    PRODUCTION = 1
    INJECTION = 2


class RateColumn(str, Enum):
    def __new__(cls, name, literal):
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.literal = literal
        return obj

    OIL = ("oil", WellMode.INJECTION)
    OIL_V = ("oil_v", WellMode.INJECTION)
    WATER_V = ("water_v", WellMode.INJECTION)
    WATER = ("water", WellMode.PRODUCTION)
    CUM_OIL_V = ("cum_oil_v", WellMode.INJECTION)
    CUM_WATER_V = ("cum_water_v", WellMode.INJECTION)
    CUM_WATER = ("cum_water", WellMode.PRODUCTION)

    def __call__(
        self, model: type[Base], mode: WellMode
    ) -> ColumnClause | Label:
        if mode is self.literal:
            return literal_column("0").label(self.value)
        return getattr(model, self.value)


def _select_separate_well_rates(model: type[Base], wmode: WellMode) -> Select:
    return select(
        select_description(model, "field").label("field"),
        select_well_name(model, "prod_uwi").label("well_name"),
        model.cid,
        select_cids().label("cid_all"),
        model.dat_rep.cast(Date),
        RateColumn.OIL(model, wmode),
        RateColumn.OIL_V(model, wmode),
        RateColumn.WATER_V(model, wmode),
        RateColumn.WATER(model, wmode),
        RateColumn.CUM_OIL_V(model, wmode),
        RateColumn.CUM_WATER_V(model, wmode),
        RateColumn.CUM_WATER(model, wmode),
        model.days,
        Reservoir.oil_compressibility.label("oil_fvf"),
    ).where(
        model.dat_rep >= bindparam("date_from"),
        model.dat_rep <= bindparam("date_to"),
        model.prod_uwi == WellStockHistExt.uwi,
        model.dat_rep == WellStockHistExt.status_date,
        model.field == HeaderId.field,
        model.uniqueid == HeaderId.uniqueid,
        model.field == Reservoir.field,
        model.cid == Reservoir.cid,
        HeaderId.district_id == Reservoir.district_id,
    )


def _select_union_rates() -> Subquery:
    subq_prod = _select_separate_well_rates(MonthlyProd, WellMode.PRODUCTION)
    subq_inj = _select_separate_well_rates(MonthlyInj, WellMode.INJECTION)
    return union(subq_prod, subq_inj).subquery()


def select_well_rates() -> Select:
    subq = _select_union_rates()
    return select(
        subq.c.field,
        subq.c.well_name,
        subq.c.cid,
        subq.c.cid_all,
        subq.c.dat_rep,
        func.sum(subq.c.oil).label("oil"),
        func.sum(subq.c.oil_v).label("oil_v"),
        func.sum(subq.c.water_v).label("water_v"),
        func.sum(subq.c.water).label("water"),
        func.sum(subq.c.cum_oil_v).label("cum_oil_v"),
        func.sum(subq.c.cum_water_v).label("cum_water_v"),
        func.sum(subq.c.cum_water).label("cum_water"),
        func.sum(subq.c.days).label("days"),
        func.min(subq.c.oil_fvf).label("oil_fvf"),
    ).group_by(
        subq.c.field,
        subq.c.well_name,
        subq.c.cid,
        subq.c.cid_all,
        subq.c.dat_rep,
    )
