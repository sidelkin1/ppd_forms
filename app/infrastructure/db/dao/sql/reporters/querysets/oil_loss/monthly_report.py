from sqlalchemy import Select, Subquery, and_, select, union

from app.infrastructure.db.dao.sql.reporters.querysets.inj_loss.monthly_report import (  # noqa
    _select_first_date,
    _select_first_rate_date,
    _select_first_report,
    _select_last_report,
    _select_max_rate_date,
)


def _join_periods(base: Subquery, pred: Subquery) -> Select:
    return select(
        base.c.field,
        base.c.well,
        base.c.reservoir,
        base.c.dat_rep.label("start_dat_rep"),
        base.c.oil_rate.label("start_oil_rate"),
        base.c.liq_rate.label("start_liq_rate"),
        base.c.watercut.label("start_watercut"),
        base.c.inj_rate.label("start_inj_rate"),
        pred.c.dat_rep.label("end_dat_rep"),
        pred.c.oil_rate.label("end_oil_rate"),
        pred.c.liq_rate.label("end_liq_rate"),
        pred.c.watercut.label("end_watercut"),
        pred.c.inj_rate.label("end_inj_rate"),
    ).outerjoin(
        pred,
        and_(
            base.c.field == pred.c.field,
            base.c.well == pred.c.well,
            base.c.reservoir == pred.c.reservoir,
        ),
    )


def select_monthly_report_for_first_rate() -> Select:
    rates = union(
        _select_first_rate_date("liq_rate"),
        _select_first_rate_date("inj_rate"),
    ).subquery()
    subq = _select_first_date(rates)
    return _join_periods(
        _select_first_report(subq).subquery(), _select_last_report().subquery()
    )


def select_monthly_report_for_max_rate() -> Select:
    rates = union(
        _select_max_rate_date("oil_rate"),
        _select_max_rate_date("inj_rate"),
    ).subquery()
    subq = _select_first_date(rates)
    return _join_periods(
        _select_first_report(subq).subquery(), _select_last_report().subquery()
    )
