from sqlalchemy import between, bindparam, func, select
from sqlalchemy.sql.expression import ScalarSelect

from app.infrastructure.db.models.ofm.reflected import (
    WellHdr,
    WellPerforations,
)

from .reservoirs import select_reservoir_ids


def select_top_perf() -> ScalarSelect:
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
