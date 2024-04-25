from sqlalchemy import Select, bindparam, func, select

from app.infrastructure.db.models.ofm.reflected import MonthlyInj


def select_cumwat() -> Select:
    return (
        select(MonthlyInj.field, MonthlyInj.uwi, func.sum(MonthlyInj.water))
        .where(MonthlyInj.field == bindparam("field_id"))
        .group_by(MonthlyInj.field, MonthlyInj.uwi)
        .order_by(MonthlyInj.uwi)
    )
