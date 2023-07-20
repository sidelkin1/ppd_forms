from datetime import date

from sqlalchemy import Date, between, distinct, func, or_, select
from sqlalchemy.sql.expression import ColumnElement, ScalarSelect, Select
from sqlalchemy.sql.functions import Function

from app.core.ofm_db import Base
from app.crud.queryset.ofm.common import select_cids, select_description
from app.models.ofm import (GeophysSt, GeophysStAbsorp, WellHdr,
                            WellLogResultLayers, WellLogResultSublayers,
                            WellOrapMd, WellPerforations, WellStockHistExt)


def _get_db_func(schema: str, name: str) -> Function:
    return getattr(getattr(func, schema), name)


def _get_str_sum(
    model: type[Base],
    schema: str,
    func_name: str,
    field: str,
) -> ColumnElement:
    db_func = _get_db_func(schema, func_name)
    return func.ofm.str_sum(distinct(db_func(getattr(model, field))))


def _check_interval_intersections(model: type[Base]) -> ColumnElement:
    return or_(
        or_(
            between(model.top,
                    GeophysStAbsorp.top,
                    GeophysStAbsorp.bottom),
            between(model.base,
                    GeophysStAbsorp.top,
                    GeophysStAbsorp.bottom),
        ),
        or_(
            between(GeophysStAbsorp.top,
                    model.top,
                    model.base),
            between(GeophysStAbsorp.bottom,
                    model.top,
                    model.base),
        ),
    )


def _calc_abs_depth(depth: str) -> ColumnElement:
    md = getattr(GeophysStAbsorp, depth)
    tvd = func.udmurtneft_n.z_get_tvd(GeophysSt.uwi, md)
    return func.round(WellHdr.elevation - tvd, 1)


def _remove_well_branch() -> ColumnElement:
    return func.decode(
        func.instr(GeophysSt.uwi, 'B'), 0,
        GeophysSt.uwi,
        WellHdr.parent_uwi,
    )


def _select_layer_perf(
    model: type[Base],
    schema: str,
    func_name: str,
    field: str,
    *where_args,
) -> ScalarSelect:
    return select(
        _get_str_sum(model, schema, func_name, field)
    ).where(
        _check_interval_intersections(model),
        *where_args,
    ).scalar_subquery().correlate(GeophysSt, GeophysStAbsorp)


def _select_cid_layers() -> ScalarSelect:
    return _select_layer_perf(
        WellOrapMd, 'udmurtneft_n', 'dg_sdes', 'reservoir_id',
        WellOrapMd.uwi == GeophysSt.uwi,
    )


def _select_layers() -> ScalarSelect:
    return _select_layer_perf(
        WellLogResultLayers, 'udmurtneft_n', 'dg_des', 'layer_id',
        WellLogResultSublayers.uwi == GeophysSt.uwi,
        WellLogResultSublayers.uwi == WellLogResultLayers.uwi,
        WellLogResultSublayers.layer_id == WellLogResultLayers.layer_id,
        WellLogResultSublayers.source == WellLogResultLayers.source,
        WellLogResultSublayers.interpreter.in_((1, 3)),
    )


def _select_perfs() -> ScalarSelect:
    return _select_layer_perf(
        WellPerforations, 'udmurtneft_n', 'dg_sdes', 'layer_id',
        WellPerforations.uwi == GeophysSt.uwi,
    )


def select_well_profiles(
    date_from: date,
    date_to: date,
) -> Select:
    return select(
        select_description(WellHdr, 'field').label('field'),
        GeophysSt.uwi,
        WellHdr.well_name,
        select_description(GeophysSt, 'prod_class').label('well_type'),
        GeophysSt.rec_date.cast(Date),
        select_cids().label('cid_all'),
        func.coalesce(
            _select_cid_layers(),
            _select_perfs()
        ).label('cid_layer'),
        _select_layers().label('layer'),
        GeophysStAbsorp.top,
        GeophysStAbsorp.bottom,
        _calc_abs_depth('top').label('abstop'),
        _calc_abs_depth('bottom').label('absbotm'),
        GeophysStAbsorp.diff_absorp,
        GeophysSt.tot_absorp,
        GeophysSt.liq_rate,
        GeophysStAbsorp.remarks,
    ).where(
        GeophysStAbsorp.id == GeophysSt.id,
        WellHdr.uwi == GeophysSt.uwi,
        WellStockHistExt.status_date == func.trunc(GeophysSt.rec_date, 'mm'),
        _remove_well_branch() == WellStockHistExt.uwi,
        GeophysSt.rec_date >= date_from,
        GeophysSt.rec_date <= date_to,
    )
