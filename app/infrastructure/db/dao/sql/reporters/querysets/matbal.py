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
    MonthlyInj,
    MonthlyInjAlt,
    MonthlyProd,
    MonthlyProdAlt,
    WellHdr,
)


def _select_field_production_rates(model: type[Base]) -> Select:
    return select(
        model.dat_rep,
        model.oil_v,
        model.water_v,
        literal_column("0").label("water"),
    ).where(
        model.field == bindparam("field_id"),
        model.cid.in_(bindparam("reservoirs")),
    )


def _select_well_production_rates(model: type[Base]) -> Select:
    return _select_field_production_rates(model).where(
        model.uwi == WellHdr.uwi, WellHdr.well_name.in_(bindparam("wells"))
    )


def _select_field_injection_rates(model: type[Base]) -> Select:
    return select(
        model.dat_rep,
        literal_column("0").label("oil_v"),
        literal_column("0").label("water_v"),
        model.water,
    ).where(
        model.field == bindparam("field_id"),
        model.cid.in_(bindparam("reservoirs")),
    )


def _select_well_injection_rates(model: type[Base]) -> Select:
    return _select_field_injection_rates(model).where(
        model.uwi == WellHdr.uwi, WellHdr.well_name.in_(bindparam("wells"))
    )


def _select_sum_rates(subq: Subquery) -> Select:
    return select(
        subq.c.dat_rep.cast(Date).label("date"),
        func.sum(subq.c.oil_v).label("Qoil"),
        func.sum(subq.c.water_v).label("Qwat"),
        func.sum(subq.c.water).label("Qinj"),
    ).group_by(subq.c.dat_rep)


def select_field_sum_rates() -> Select:
    subq_prod = _select_field_production_rates(MonthlyProd)
    subq_inj = _select_field_injection_rates(MonthlyInj)
    return _select_sum_rates(union_all(subq_prod, subq_inj).subquery())


def select_well_sum_rates() -> Select:
    subq_prod = _select_well_production_rates(MonthlyProd)
    subq_inj = _select_well_injection_rates(MonthlyInj)
    return _select_sum_rates(union_all(subq_prod, subq_inj).subquery())


def select_field_sum_alternative_rates() -> Select:
    subq_prod = _select_field_production_rates(MonthlyProdAlt)
    subq_inj = _select_field_injection_rates(MonthlyInjAlt)
    return _select_sum_rates(union_all(subq_prod, subq_inj).subquery())


def select_well_sum_alternative_rates() -> Select:
    subq_prod = _select_well_production_rates(MonthlyProdAlt)
    subq_inj = _select_well_injection_rates(MonthlyInjAlt)
    return _select_sum_rates(union_all(subq_prod, subq_inj).subquery())
