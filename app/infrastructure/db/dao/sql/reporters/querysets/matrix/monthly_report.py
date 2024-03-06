from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import MonthlyReport


def select_monthly_report() -> Select:
    return select(
        MonthlyReport.field,
        MonthlyReport.well_name.label("well"),
        MonthlyReport.cid.label("reservoir"),
        MonthlyReport.dat_rep,
        MonthlyReport.oil_rate,
        MonthlyReport.liq_rate,
        MonthlyReport.watercut,
        MonthlyReport.inj_rate,
        MonthlyReport.liquid_res,
        MonthlyReport.cum_liquid_res,
        MonthlyReport.water,
        MonthlyReport.cum_water,
    ).where(
        MonthlyReport.dat_rep >= bindparam("mer_date_from"),
        MonthlyReport.dat_rep <= bindparam("mer_date_to"),
    )
