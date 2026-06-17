from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import ScalarSelect

from app.infrastructure.db.models.ofm.reflected import WellHdr, WellMonthHist

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


def select_watercut() -> ScalarSelect:
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
