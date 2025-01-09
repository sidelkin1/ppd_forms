from sqlalchemy import bindparam, func, literal_column, or_, select, union
from sqlalchemy.orm import QueryableAttribute
from sqlalchemy.sql.expression import CompoundSelect, Select, Subquery

from app.infrastructure.db.models.local import MonthlyReport


def _select_max_rate(rate: QueryableAttribute) -> Subquery:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
            func.max(rate).label("max_rate"),
        )
        .where(
            MonthlyReport.dat_rep >= bindparam("date_from"),
            MonthlyReport.dat_rep <= bindparam("date_to"),
            rate > 0,
        )
        .group_by(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
        )
        .subquery()
    )


def _select_first_rate_date(rate: QueryableAttribute) -> Select:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
            func.min(MonthlyReport.dat_rep).label("first_date"),
        )
        .where(
            MonthlyReport.dat_rep >= bindparam("date_from"),
            MonthlyReport.dat_rep <= bindparam("date_to"),
            rate > 0,
        )
        .group_by(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid,
        )
    )


def _select_max_rate_date(rate: QueryableAttribute) -> Select:
    subq = _select_max_rate(rate)
    return select(
        MonthlyReport.field,
        MonthlyReport.well_name,
        MonthlyReport.cid,
        MonthlyReport.dat_rep.label("first_date"),
    ).where(
        MonthlyReport.field == subq.c.field,
        MonthlyReport.well_name == subq.c.well_name,
        MonthlyReport.cid == subq.c.cid,
        rate == subq.c.max_rate,
        MonthlyReport.dat_rep >= bindparam("date_from"),
        MonthlyReport.dat_rep <= bindparam("date_to"),
    )


def _select_first_date(rates: Subquery) -> Subquery:
    return (
        select(
            rates.c.field,
            rates.c.well_name,
            rates.c.cid,
            func.max(rates.c.first_date).label("min_date"),
        )
        .group_by(
            rates.c.field,
            rates.c.well_name,
            rates.c.cid,
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


def _select_first_report(subq: Subquery) -> Select:
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
        MonthlyReport.field == subq.c.field,
        MonthlyReport.well_name == subq.c.well_name,
        MonthlyReport.cid == subq.c.cid,
        MonthlyReport.dat_rep == subq.c.min_date,
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


def select_monthly_report_for_first_rate() -> CompoundSelect:
    rates = union(
        _select_first_rate_date(MonthlyReport.liq_rate),
        _select_first_rate_date(MonthlyReport.inj_rate),
    ).subquery()
    subq = _select_first_date(rates)
    return union(_select_first_report(subq), _select_last_report())


def select_monthly_report_for_max_rate() -> CompoundSelect:
    rates = union(
        _select_max_rate_date(MonthlyReport.oil_rate),
        _select_max_rate_date(MonthlyReport.inj_rate),
    ).subquery()
    subq = _select_first_date(rates)
    return union(_select_first_report(subq), _select_last_report())
