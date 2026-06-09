from sqlalchemy import between, bindparam, func, select
from sqlalchemy.sql.expression import (
    ScalarSelect,
    Select,
    Subquery,
)

from app.infrastructure.db.models.ofm.reflected import (
    Reservoir2,
    ResPty,
    WellHdr,
    WellMonthHist,
    WellPerforations,
    WellStockHist,
)

from .branches import select_well_branch
from .reservoirs import select_reservoir_ids


def _select_max_mer_date() -> ScalarSelect:
    return (
        select(func.max(WellMonthHist.start_date).label("max_date"))
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(select_reservoir_ids()),
            WellMonthHist.start_date <= bindparam("on_date"),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def _select_max_stock_date() -> Subquery:
    return (
        select(
            WellStockHist.uwi,
            func.max(WellStockHist.status_date).label("max_date"),
        )
        .where(
            WellStockHist.status_date <= bindparam("on_date"),
        )
        .group_by(WellStockHist.uwi)
        .subquery()
    )


def _select_well_stock_hist() -> Subquery:
    subq = _select_max_stock_date()
    return (
        select(
            WellStockHist.uwi,
            WellStockHist.prod_class,
            WellStockHist.prod_method,
            WellStockHist.status,
        )
        .where(
            WellStockHist.uwi == subq.c.uwi,
            WellStockHist.status_date == subq.c.max_date,
        )
        .subquery()
    )


def _select_watercut() -> ScalarSelect:
    return (
        select(
            func.decode(
                func.sum(WellMonthHist.water_v + WellMonthHist.oil_v),
                None,
                100,
                0,
                100,
                func.sum(WellMonthHist.water_v)
                / func.sum(WellMonthHist.water_v + WellMonthHist.oil_v)
                * 100,
            )
        )
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(select_reservoir_ids()),
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
            WellPerforations.layer_id.in_(select_reservoir_ids()),
            between(
                bindparam("on_date"),
                WellPerforations.comp_date,
                WellPerforations.close_date,
            ),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def select_properties() -> Select:
    stock = _select_well_stock_hist()
    return select(
        func.udmurtneft_n.dg_des(bindparam("field_id")).label("field"),
        bindparam("well").label("well"),
        WellHdr.well_name.label("branch"),
        func.udmurtneft_n.dg_des(bindparam("reservoir_id")).label("reservoir"),
        bindparam("on_date").label("on_date"),
        WellHdr.elevation,
        func.abs(ResPty.abs_depth_owc).label("abs_depth_owc"),
        ResPty.layer_oil_density,
        ResPty.water_density,
        _select_watercut().label("watercut"),
        _select_top_perf().label("top_perf"),
        func.udmurtneft_n.dg_des(WellHdr.operator).label("region"),
        func.udmurtneft_n.dg_des(WellHdr.agent).label("workshop"),
        WellHdr.rig_no.label("pad"),
        func.udmurtneft_n.dg_des(WellHdr.hole_direction).label("wellbore"),
        func.udmurtneft_n.dg_des(stock.c.prod_class).label("well_mode"),
        func.udmurtneft_n.dg_sdes(stock.c.prod_method).label("well_lift"),
        func.udmurtneft_n.dg_sdes(stock.c.status).label("well_status"),
    ).where(
        WellHdr.uwi.in_(select_well_branch()),
        Reservoir2.reservoir_id == bindparam("reservoir_id"),
        Reservoir2.field_code == WellHdr.field,
        Reservoir2.district == WellHdr.district,
        Reservoir2.existence_type == "ACTUAL",
        ResPty.reservoir_s == Reservoir2.reservoir_s,
        stock.c.uwi == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
    )
