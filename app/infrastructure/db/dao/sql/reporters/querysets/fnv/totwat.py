from sqlalchemy import Select, bindparam, func, select

from app.infrastructure.db.models.ofm.reflected import MonthlyInj


def select_totwat() -> Select:
    return select(func.sum(MonthlyInj.water).label("totwat")).where(
        MonthlyInj.uwi == bindparam("uwi"),
        MonthlyInj.dat_rep
        >= func.to_date(bindparam("date_from"), "YYYY-MM-DD"),
        MonthlyInj.dat_rep < func.to_date(bindparam("date_to"), "YYYY-MM-DD"),
    )
