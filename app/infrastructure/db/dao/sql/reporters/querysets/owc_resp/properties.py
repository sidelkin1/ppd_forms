from sqlalchemy import bindparam, func, select, table, union
from sqlalchemy.sql.expression import (
    CompoundSelect,
    ScalarSelect,
    Select,
    Subquery,
)

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    Reservoir2,
    ResPty,
    WellHdr,
    WellMonthHist,
    WellPerforations,
)


def _select_reservoir_ids() -> CompoundSelect:
    return union(
        select(bindparam("reservoir_id").label("reservoir")).select_from(
            table("dual")
        ),
        select(DictG.id.label("reservoir")).where(
            DictG.mr == func.to_char(bindparam("reservoir_id"))
        ),
    )


def _select_max_mer_date() -> Subquery:
    return (
        select(func.max(WellMonthHist.start_date).label("max_date"))
        .where(
            WellMonthHist.uwi == WellHdr.uwi,
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
        )
        .subquery()
    )


def _select_watercut() -> ScalarSelect:
    subq = _select_max_mer_date()
    return (
        select(
            func.sum(WellMonthHist.water_v)
            / func.sum(WellMonthHist.water_v + WellMonthHist.oil_v)
        )
        .where(
            WellMonthHist.uwi == WellHdr.uwi,
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
            WellMonthHist.start_date == subq.c.max_date,
        )
        .scalar_subquery()
    )


def _select_top_perf() -> ScalarSelect:
    return (
        select(func.min(WellPerforations.top))
        .where(
            WellPerforations.uwi == WellHdr.uwi,
            WellPerforations.layer_id.in_(_select_reservoir_ids()),
            WellPerforations.close_date == func.to_date("01.01.3000"),
        )
        .scalar_subquery()
    )


def select_properties() -> Select:
    return select(
        WellHdr.elevation,
        ResPty.abs_depth_owc,
        ResPty.layer_oil_density,
        ResPty.water_density,
        _select_watercut().label("watercut"),
        _select_top_perf().label("top_perf"),
    ).where(
        WellHdr.well_name == bindparam("well"),
        WellHdr.field == bindparam("field_id"),
        Reservoir2.reservoir_id == bindparam("reservoir_id"),
        Reservoir2.field_code == WellHdr.field,
        Reservoir2.district == WellHdr.district,
        Reservoir2.existence_type == "ACTUAL",
        ResPty.reservoir_s == Reservoir2.reservoir_s,
    )
