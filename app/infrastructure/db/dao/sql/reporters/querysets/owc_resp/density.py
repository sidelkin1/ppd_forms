from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import ScalarSelect

from app.infrastructure.db.models.ofm.udmurtneft_n import (
    WellHdr,
    WellMonthHist,
    WellMonthHistPty,
)

from .reservoirs import select_reservoir_ids

_WATER_DENSITY_IDS = (1238899, 1238979)


def _select_max_rec_id() -> ScalarSelect:
    return (
        select(func.max(WellMonthHist.rec_id).label("max_rec_id"))
        .where(
            WellMonthHist.uwi
            == func.coalesce(WellHdr.parent_uwi, WellHdr.uwi),
            WellMonthHist.layer_id.in_(select_reservoir_ids()),
            WellMonthHist.start_date <= bindparam("on_date"),
            WellMonthHistPty.wmh_id == WellMonthHist.rec_id,
            WellMonthHistPty.parameter_id.in_(_WATER_DENSITY_IDS),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )


def select_water_density() -> ScalarSelect:
    return (
        select(func.min(WellMonthHistPty.num_val).label("water_density"))
        .where(
            WellMonthHistPty.wmh_id == _select_max_rec_id(),
            WellMonthHistPty.parameter_id.in_(_WATER_DENSITY_IDS),
        )
        .scalar_subquery()
        .correlate(WellHdr)
    )
