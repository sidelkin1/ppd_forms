from sqlalchemy import (
    Date,
    Select,
    Subquery,
    bindparam,
    func,
    literal_column,
    select,
    union_all,
)

from app.infrastructure.db.models.ofm.base import Base
from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    MonthlyInj,
    MonthlyInjAlt,
    MonthlyProd,
    MonthlyProdAlt,
    WellHdr,
)


def _select_production_rates(model: type[Base]) -> Select:
    return select(
        DictG.description,
        WellHdr.well_name,
        model.cid,
        model.dat_rep,
        model.oil_v,
        model.water_v,
        literal_column("0").label("water"),
    ).where(
        model.field == DictG.id,
        model.uwi == WellHdr.uwi,
        (DictG.description + WellHdr.well_name + model.cid).in_(
            bindparam("uids")
        ),
    )


def _select_injection_rates(model: type[Base]) -> Select:
    return select(
        DictG.description,
        WellHdr.well_name,
        model.cid,
        model.dat_rep,
        literal_column("0").label("oil_v"),
        literal_column("0").label("water_v"),
        model.water,
    ).where(
        model.field == DictG.id,
        model.uwi == WellHdr.uwi,
        (DictG.description + WellHdr.well_name + model.cid).in_(
            bindparam("uids")
        ),
    )


def _select_sum_rates(subq: Subquery) -> Select:
    return select(
        subq.c.description.label("Field"),
        subq.c.well_name.label("Well"),
        subq.c.cid.label("Reservoir"),
        subq.c.dat_rep.cast(Date).label("Date"),
        func.sum(subq.c.oil_v).label("Qoil"),
        func.sum(subq.c.water_v).label("Qwat"),
        func.sum(subq.c.water).label("Qinj"),
    ).group_by(
        subq.c.description,
        subq.c.well_name,
        subq.c.cid,
        subq.c.dat_rep,
    )


def select_tank_rates() -> Select:
    prod = _select_production_rates(MonthlyProd)
    inj = _select_injection_rates(MonthlyInj)
    return _select_sum_rates(union_all(prod, inj).subquery())


def select_tank_alternative_rates() -> Select:
    prod = _select_production_rates(MonthlyProdAlt)
    inj = _select_injection_rates(MonthlyInjAlt)
    return _select_sum_rates(union_all(prod, inj).subquery())
