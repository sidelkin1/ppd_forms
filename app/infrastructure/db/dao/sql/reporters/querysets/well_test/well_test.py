from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import WellTest


def select_well_tests() -> Select:
    return (
        select(
            WellTest.field,
            WellTest.well,
            WellTest.reservoir,
            WellTest.well_type,
            WellTest.well_test,
            WellTest.end_date,
            WellTest.resp_owc,
            func.coalesce(
                WellTest.liq_perm, WellTest.oil_perm, WellTest.wat_perm
            ).label("permeability"),
            WellTest.skin_factor,
            WellTest.prod_index,
        )
        .where(
            WellTest.field == bindparam("field"),
            WellTest.well == bindparam("well"),
            WellTest.reservoir.in_(bindparam("reservoirs")),
            WellTest.end_date < bindparam("report_date"),
        )
        .order_by(WellTest.reservoir, WellTest.end_date)
    )
