from enum import Enum

from sqlalchemy import bindparam, func, select, table, union
from sqlalchemy.sql.expression import CompoundSelect, ScalarSelect, Select

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    Reservoir2,
    ResPty,
    WellHdr,
    WellMonthHist,
    WellPerforations,
)


class _ProdClass(Enum):
    absorb = 7810
    prod = 26690
    inj = 42770
    water = 80070


def _select_reservoir_ids() -> CompoundSelect:
    return union(
        select(bindparam("reservoir_id").label("reservoir")).select_from(
            table("dual")
        ),
        select(DictG.id.label("reservoir")).where(
            DictG.mr == func.to_char(bindparam("reservoir_id"))
        ),
    )


def _select_max_mer_date() -> ScalarSelect:
    return (
        select(func.max(WellMonthHist.start_date).label("max_date"))
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def _select_max_prod_date() -> ScalarSelect:
    return (
        select(func.max(WellMonthHist.start_date).label("max_date"))
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
            WellMonthHist.prod_class == _ProdClass.prod.value,
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def _select_watercut() -> ScalarSelect:
    return (
        select(
            func.sum(WellMonthHist.water_v)
            / func.sum(WellMonthHist.water_v + WellMonthHist.oil_v)
            * 100
        )
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
            WellMonthHist.start_date == _select_max_prod_date(),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def _select_well_mode() -> ScalarSelect:
    return (
        select(func.min(WellMonthHist.prod_class))
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(_select_reservoir_ids()),
            WellMonthHist.start_date == _select_max_mer_date(),
        )
        .scalar_subquery()
        .correlate(WellHdr)
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
        .correlate(WellHdr)
    )


def select_properties() -> Select:
    return select(
        func.udmurtneft_n.dg_sdes(WellHdr.class_).label("well_mode"),
        WellHdr.elevation,
        -ResPty.abs_depth_owc,
        ResPty.layer_oil_density,
        ResPty.water_density,
        func.decode(
            _select_well_mode(),
            _ProdClass.absorb.value,
            100,
            _ProdClass.inj.value,
            100,
            _ProdClass.water.value,
            100,
            _select_watercut(),
        ).label("watercut"),
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
