from sqlalchemy import and_, bindparam, func, or_, select
from sqlalchemy.sql.expression import ScalarSelect, Select, Subquery

from app.infrastructure.db.models.local import MonthlyReport, WellProfile


def _select_sum_absorb() -> Subquery:
    return (
        select(
            WellProfile.uwi,
            WellProfile.cid_all,
            WellProfile.rec_date,
            func.sum(WellProfile.diff_absorp).label("total_absorp"),
        )
        .group_by(
            WellProfile.uwi,
            WellProfile.cid_all,
            WellProfile.rec_date,
        )
        .subquery()
    )


def _select_profile_date() -> Subquery:
    subq = _select_sum_absorb()
    return (
        select(
            subq.c.uwi,
            subq.c.cid_all,
            func.max(subq.c.rec_date).label("max_date"),
        )
        .where(
            subq.c.total_absorp > 0,
        )
        .group_by(
            subq.c.uwi,
            subq.c.cid_all,
        )
        .subquery()
    )


def _select_last_profile() -> Subquery:
    stmt = _select_profile_date()
    return (
        select(
            WellProfile.field,
            WellProfile.well_name,
            WellProfile.well_type,
            WellProfile.cid_all,
            WellProfile.rec_date,
            WellProfile.layer,
            WellProfile.diff_absorp,
            WellProfile.remarks,
        )
        .where(
            WellProfile.uwi == stmt.c.uwi,
            WellProfile.rec_date == stmt.c.max_date,
        )
        .subquery()
    )


def _select_last_report() -> Subquery:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid_all,
            func.max(MonthlyReport.dat_rep).label("max_date"),
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
            MonthlyReport.cid_all,
        )
        .subquery()
    )


def _select_sum_rate(rate: str) -> Subquery:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.dat_rep,
            func.sum(getattr(MonthlyReport, rate)).label(f"{rate}_all"),
        )
        .group_by(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.dat_rep,
        )
        .subquery()
    )


def _select_sum_value(rate: str) -> ScalarSelect:
    stmt = _select_sum_rate(rate)
    return (
        select(getattr(stmt.c, f"{rate}_all"))
        .where(
            stmt.c.field == MonthlyReport.field,
            stmt.c.well_name == MonthlyReport.well_name,
            stmt.c.dat_rep == MonthlyReport.dat_rep,
        )
        .scalar_subquery()
        .correlate(MonthlyReport)
    )


def select_profile_report() -> Select:
    last_report = _select_last_report()
    last_profile = _select_last_profile()
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.cid_all,
            MonthlyReport.cid,
            MonthlyReport.dat_rep,
            MonthlyReport.liq_rate,
            MonthlyReport.inj_rate,
            _select_sum_value("liq_rate").label("liq_rate_all"),
            _select_sum_value("inj_rate").label("inj_rate_all"),
            last_profile.c.well_type,
            last_profile.c.rec_date,
            last_profile.c.layer,
            last_profile.c.diff_absorp,
            last_profile.c.remarks,
        )
        .where(
            MonthlyReport.field == last_report.c.field,
            MonthlyReport.well_name == last_report.c.well_name,
            MonthlyReport.cid_all == last_report.c.cid_all,
            MonthlyReport.dat_rep == last_report.c.max_date,
        )
        .outerjoin(
            last_profile,
            and_(
                last_profile.c.field == MonthlyReport.field,
                last_profile.c.well_name == MonthlyReport.well_name,
                last_profile.c.cid_all == MonthlyReport.cid_all,
            ),
        )
    )
