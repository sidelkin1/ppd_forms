from typing import Any

from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import ColumnElement, Select, Subquery

from app.infrastructure.db.dao.query.ofm.querysets.common import (
    select_cids,
    select_description,
)
from app.infrastructure.db.models.ofm.reflected import (
    GeophysSt,
    GeophysStAbsorp,
    WellHdr,
    WellStockHistExt,
)


def _remove_well_branch() -> ColumnElement:
    return func.decode(
        func.instr(GeophysSt.uwi, "B"), 0, GeophysSt.uwi, WellHdr.parent_uwi
    )


def start_date_of_year(input_date: Any) -> ColumnElement:
    return func.trunc(input_date, "year")


def end_date_of_year(input_date: Any) -> ColumnElement:
    return func.add_months(start_date_of_year(input_date), 12) - 1


def _select_profile_id() -> Subquery:
    return select(GeophysStAbsorp.id).distinct().subquery()


def select_well_profiles() -> Select:
    profiles = _select_profile_id()
    return select(
        select_description(WellHdr, "field").label("field"),
        WellHdr.well_name,
        select_description(GeophysSt, "prod_class").label("well_type"),
        GeophysSt.rec_date,
        func.concat(select_cids(), " all").label("reservoir"),
    ).where(
        profiles.c.id == GeophysSt.id,
        WellHdr.uwi == GeophysSt.uwi,
        WellStockHistExt.status_date == func.trunc(GeophysSt.rec_date, "mm"),
        _remove_well_branch() == WellStockHistExt.uwi,
        GeophysSt.rec_date >= start_date_of_year(bindparam("date_from")),
        GeophysSt.rec_date <= end_date_of_year(bindparam("date_to")),
    )
