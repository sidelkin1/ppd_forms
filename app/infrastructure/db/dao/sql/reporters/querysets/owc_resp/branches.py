from sqlalchemy import between, bindparam, func, select
from sqlalchemy.sql.expression import ScalarSelect, Select

from app.infrastructure.db.models.ofm.reflected import (
    WellHdr,
    WellPerforations,
)

from .reservoirs import select_reservoir_ids


def _select_well_uwi() -> Select:
    return select(WellHdr.uwi).where(
        WellHdr.well_name == bindparam("well"),
        WellHdr.field == bindparam("field_id"),
    )


def _select_well_uwi_with_open_perf() -> ScalarSelect:
    subq = _select_well_uwi().subquery()
    return (
        select(func.min(WellPerforations.uwi).label("uwi"))
        .where(
            WellPerforations.uwi.like(func.concat(subq.c.uwi, "%")),
            between(
                bindparam("on_date"),
                WellPerforations.comp_date,
                WellPerforations.close_date,
            ),
            WellPerforations.layer_id.in_(select_reservoir_ids()),
        )
        .scalar_subquery()
    )


def select_well_branch() -> Select:
    subq1 = _select_well_uwi().scalar_subquery()
    subq2 = _select_well_uwi_with_open_perf()
    return select(func.coalesce(subq2, subq1).label("uwi"))
