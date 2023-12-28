from sqlalchemy import and_, func, or_, select
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.local import InjWellDatabase, MonthlyReport


def _select_last_report() -> Subquery:
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            func.max(MonthlyReport.dat_rep).label("max_date"),
        )
        .where(
            or_(
                MonthlyReport.water > 0,
                MonthlyReport.liquid > 0,
            ),
        )
        .group_by(
            MonthlyReport.field,
            MonthlyReport.well_name,
        )
        .subquery()
    )


def _select_last_cid() -> Subquery:
    last_report = _select_last_report()
    return (
        select(
            MonthlyReport.field,
            MonthlyReport.well_name,
            MonthlyReport.dat_rep,
            MonthlyReport.cid_all,
        )
        .where(
            MonthlyReport.field == last_report.c.field,
            MonthlyReport.well_name == last_report.c.well_name,
            MonthlyReport.dat_rep == last_report.c.max_date,
        )
        .distinct()
        .subquery()
    )


def select_inj_well_database() -> Select:
    last_cid = _select_last_cid()
    return select(
        InjWellDatabase.field,
        InjWellDatabase.well,
        last_cid.c.dat_rep,
        last_cid.c.cid_all.label("reservoir"),
    ).outerjoin(
        last_cid,
        and_(
            last_cid.c.field == InjWellDatabase.field,
            last_cid.c.well_name == InjWellDatabase.well,
        ),
    )
