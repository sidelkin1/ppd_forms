from sqlalchemy import bindparam, case, func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import WellTest


def select_well_tests() -> Select:
    return (
        select(
            WellTest.field,
            case(
                (
                    WellTest.layer.is_(None),
                    WellTest.well,
                ),
                else_=func.concat(
                    WellTest.well,
                    " (",
                    WellTest.layer,
                    ")",
                ),
            ).label("well"),
            WellTest.reservoir,
            WellTest.well_type,
            WellTest.well_test,
            WellTest.end_date,
            WellTest.resp_owc,
            func.coalesce(
                WellTest.liq_perm, WellTest.oil_perm, WellTest.wat_perm
            ).label("permeability"),
            case(
                (
                    WellTest.well_test.in_(("КВУ", "КПД", "КВД", "КСД")),
                    func.coalesce(WellTest.skin_factor, 0),
                ),
                else_=WellTest.skin_factor,
            ).label("skin_factor"),
            WellTest.prod_index,
            WellTest.frac_length,
            case(
                (WellTest.reliability == "НЕИЗВЕСТНО", "-"),
                else_=WellTest.reliability,
            ).label("reliability"),
        )
        .where(
            WellTest.field == bindparam("field"),
            WellTest.well == bindparam("well"),
            WellTest.reservoir.in_(bindparam("reservoirs")),
            WellTest.end_date < bindparam("report_date"),
        )
        .order_by(WellTest.reservoir, WellTest.end_date)
    )
