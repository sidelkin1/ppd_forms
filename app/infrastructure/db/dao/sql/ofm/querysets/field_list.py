from sqlalchemy import func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    MonthlyInj,
    MonthlyProd,
)


def select_fields() -> Select:
    return (
        select(DictG.id, DictG.description.label("name"))
        .where(DictG.grp == 1670, DictG.code.is_not(None))
        .order_by("name")
    )


def select_production_fields() -> Select:
    subq = (
        select(MonthlyProd.field)
        .where((MonthlyProd.oil_v + MonthlyProd.water_v) > 0)
        .distinct()
        .subquery()
    )
    return select(
        subq.c.field.label("id"),
        func.udmurtneft_n.dg_des(subq.c.field).label("name"),
    ).order_by("name")


def select_injection_fields() -> Select:
    subq = (
        select(MonthlyInj.field)
        .where(MonthlyInj.water > 0)
        .distinct()
        .subquery()
    )
    return select(
        subq.c.field.label("id"),
        func.udmurtneft_n.dg_des(subq.c.field).label("name"),
    ).order_by("name")
