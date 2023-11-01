from sqlalchemy import bindparam, func, literal_column, or_, select, union
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.local import MonthlyReport


def _select_first_date() -> Subquery:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
            func.min(MonthlyReport.dat_rep).label("min_date"),
        )
        .where(
            MonthlyReport.dat_rep >= bindparam("date_from"),
            MonthlyReport.dat_rep <= bindparam("date_to"),
            or_(
                MonthlyReport.water > 0,
                MonthlyReport.liquid > 0,
            ),
        )
        .group_by(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
        )
        .subquery()
    )


def _select_last_date() -> Subquery:
    return (
        select(func.max(MonthlyReport.dat_rep).label("max_date"))
        .where(
            MonthlyReport.dat_rep >= bindparam("date_from"),
            MonthlyReport.dat_rep <= bindparam("date_to"),
        )
        .subquery()
    )


def _select_first_report() -> Select:
    first_date = _select_first_date()
    return select(
        MonthlyReport.field,
        MonthlyReport.well_name.label("well"),
        MonthlyReport.cid.label("reservoir"),
        MonthlyReport.dat_rep,
        MonthlyReport.oil_rate,
        MonthlyReport.liq_rate,
        MonthlyReport.watercut,
        MonthlyReport.inj_rate,
        literal_column("'start'").label("period"),
    ).where(
        MonthlyReport.field == first_date.c.field,
        MonthlyReport.well_name == first_date.c.well_name,
        MonthlyReport.cid == first_date.c.cid,
        MonthlyReport.dat_rep == first_date.c.min_date,
    )


def _select_last_report() -> Select:
    last_date = _select_last_date()
    return select(
        MonthlyReport.field,
        MonthlyReport.well_name.label("well"),
        MonthlyReport.cid.label("reservoir"),
        MonthlyReport.dat_rep,
        MonthlyReport.oil_rate,
        MonthlyReport.liq_rate,
        MonthlyReport.watercut,
        MonthlyReport.inj_rate,
        literal_column("'end'").label("period"),
    ).where(
        MonthlyReport.dat_rep == last_date.c.max_date,
        or_(
            MonthlyReport.water > 0,
            MonthlyReport.liquid > 0,
        ),
    )


def select_monthly_report() -> Select:
    return union(_select_first_report(), _select_last_report())
