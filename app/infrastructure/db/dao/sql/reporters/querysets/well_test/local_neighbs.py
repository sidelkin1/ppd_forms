from sqlalchemy import bindparam, func, select
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.local import WellTest


def _select_last_well_tests() -> Subquery:
    return (
        select(
            WellTest.field,
            WellTest.well,
            WellTest.reservoir,
            func.max(WellTest.end_date).label("max_date"),
        )
        .where(
            func.concat(
                WellTest.field,
                WellTest.well,
                WellTest.reservoir,
            ).in_(bindparam("uids")),
            WellTest.end_date >= bindparam("date_from"),
            WellTest.end_date <= bindparam("report_date"),
        )
        .group_by(
            WellTest.field,
            WellTest.well,
            WellTest.reservoir,
        )
    ).subquery()


def select_neighb_tests() -> Select:
    subq = _select_last_well_tests()
    return (
        select(
            WellTest.field,
            WellTest.well,
            WellTest.reservoir,
            WellTest.well_type,
            WellTest.well_test,
            WellTest.end_date,
            WellTest.resp_owc,
        )
        .where(
            WellTest.field == subq.c.field,
            WellTest.well == subq.c.well,
            WellTest.reservoir == subq.c.reservoir,
            WellTest.end_date == subq.c.max_date,
        )
        .order_by(WellTest.reservoir, WellTest.end_date)
    )
