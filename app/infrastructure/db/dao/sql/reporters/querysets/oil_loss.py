from sqlalchemy import Select, Subquery, and_, bindparam, func, select, union

from app.infrastructure.db.dao.sql.reporters.querysets.inj_loss.monthly_report import (  # noqa
    _select_first_date,
    _select_first_rate_date,
    _select_first_report,
    _select_last_report,
    _select_max_rate_date,
)
from app.infrastructure.db.models.local import NewStrategyOil


def _select_last_gtm() -> Subquery:
    return (
        select(
            NewStrategyOil.field,
            NewStrategyOil.well,
            func.max(NewStrategyOil.vnr_date).label("max_date"),
        )
        .where(
            NewStrategyOil.vnr_date >= bindparam("date_from"),
            NewStrategyOil.vnr_date <= bindparam("date_to"),
        )
        .group_by(
            NewStrategyOil.field,
            NewStrategyOil.well,
        )
        .subquery()
    )


def _select_new_strategy_oil() -> Subquery:
    last_gtm = _select_last_gtm()
    return (
        select(
            NewStrategyOil.field,
            NewStrategyOil.well,
            NewStrategyOil.reservoir_after,
            NewStrategyOil.vnr_date,
            NewStrategyOil.gtm_name,
        )
        .where(
            NewStrategyOil.field == last_gtm.c.field,
            NewStrategyOil.well == last_gtm.c.well,
            NewStrategyOil.vnr_date == last_gtm.c.max_date,
        )
        .subquery()
    )


def _join_periods(base: Subquery, pred: Subquery, ns_oil: Subquery) -> Select:
    return (
        select(
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
            ns_oil.c.vnr_date,
            ns_oil.c.reservoir_after,
            ns_oil.c.gtm_name,
        )
        .outerjoin(
            pred,
            and_(
                base.c.field == pred.c.field,
                base.c.well == pred.c.well,
                base.c.reservoir == pred.c.reservoir,
            ),
        )
        .outerjoin(
            ns_oil,
            and_(
                base.c.field == ns_oil.c.field,
                base.c.well == ns_oil.c.well,
            ),
        )
    )


def select_monthly_report_for_first_rate() -> Select:
    rates = union(
        _select_first_rate_date("liq_rate"),
        _select_first_rate_date("inj_rate"),
    ).subquery()
    subq = _select_first_date(rates)
    return _join_periods(
        _select_first_report(subq).subquery(),
        _select_last_report().subquery(),
        _select_new_strategy_oil(),
    )


def select_monthly_report_for_max_rate() -> Select:
    rates = union(
        _select_max_rate_date("oil_rate"),
        _select_max_rate_date("inj_rate"),
    ).subquery()
    subq = _select_first_date(rates)
    return _join_periods(
        _select_first_report(subq).subquery(),
        _select_last_report().subquery(),
        _select_new_strategy_oil(),
    )
