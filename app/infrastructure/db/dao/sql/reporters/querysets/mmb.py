from sqlalchemy import (
    Date,
    Select,
    Subquery,
    and_,
    bindparam,
    func,
    literal_column,
    or_,
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
    Pressure,
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
        DictG.description.in_(bindparam("fields")),
        model.cid.in_(bindparam("reservoirs")),
        model.uwi == WellHdr.uwi,
        WellHdr.well_name.in_(bindparam("wells")),
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
        DictG.description.in_(bindparam("fields")),
        model.cid.in_(bindparam("reservoirs")),
        model.uwi == WellHdr.uwi,
        WellHdr.well_name.in_(bindparam("wells")),
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
        subq.c.description, subq.c.well_name, subq.c.cid, subq.c.dat_rep
    )


def _select_reservoir_pressure() -> Subquery:
    return (
        select(
            DictG.description.label("Field"),
            WellHdr.well_name.label("Well"),
            Pressure.cid.label("Reservoir"),
            func.trunc(Pressure.test_date, "month").cast(Date).label("Date"),
            Pressure.source.label("Source_resp"),
            func.coalesce(
                Pressure.owc_resp_arm,
                Pressure.owc_resp_in1p,
                Pressure.owc_resp_inwt,
            ).label("Pres"),
        )
        .where(
            or_(
                Pressure.owc_resp_arm.is_not(None),
                Pressure.owc_resp_in1p.is_not(None),
                Pressure.owc_resp_inwt.is_not(None),
            ),
            Pressure.source.in_(("Сиам", "OIS Gen", "Геолог УН")),
        )
        .subquery()
    )


def _select_all(prod: Select, inj: Select) -> Select:
    resp = _select_reservoir_pressure()
    rates = _select_sum_rates(union_all(prod, inj).subquery())
    return rates.outerjoin(
        resp,
        and_(
            rates.c.Field == resp.c.Field,
            rates.c.Well == resp.c.Well,
            rates.c.Reservoir == resp.c.Reservoir,
            rates.c.Date == resp.c.Date,
        ),
    )


def select_tank_history() -> Select:
    subq_prod = _select_production_rates(MonthlyProd)
    subq_inj = _select_injection_rates(MonthlyInj)
    return _select_all(subq_prod, subq_inj)


def select_tank_alternative_history() -> Select:
    subq_prod = _select_production_rates(MonthlyProdAlt)
    subq_inj = _select_injection_rates(MonthlyInjAlt)
    return _select_all(subq_prod, subq_inj)
