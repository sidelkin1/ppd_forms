from datetime import date
from enum import Enum

from sqlalchemy import Date, func, literal_column, select, union
from sqlalchemy.sql.expression import ColumnClause, Select, Subquery

from app.core.ofm_db import Base
from app.crud.queryset.ofm.common import (select_cids, select_description,
                                          select_well_name)
from app.models.ofm import MonthlyInj, MonthlyProd, WellStockHistExt


class WellMode(Enum):
    PRODUCTION = 1
    INJECTION = 2


class RateColumn(str, Enum):

    def __new__(cls, name, literal):
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.literal = literal
        return obj

    OIL_V = ('oil_v', WellMode.INJECTION)
    WATER_V = ('water_v', WellMode.INJECTION)
    WATER = ('water', WellMode.PRODUCTION)

    def __call__(self, model: type[Base], mode: WellMode) -> ColumnClause:
        if mode is self.literal:
            return literal_column('0').label(self.value)
        return getattr(model, self.value)


def select_separate_well_rates(
    model: type[Base],
    wmode: WellMode,
    date_from: date,
    date_to: date,
) -> Select:
    return select(
        select_description(model, 'field').label('field'),
        select_well_name(model, 'prod_uwi').label('well_name'),
        model.cid,
        select_cids().label('cid_all'),
        model.dat_rep.cast(Date),
        RateColumn.OIL_V(model, wmode),
        RateColumn.WATER_V(model, wmode),
        RateColumn.WATER(model, wmode),
        model.days,
    ).where(
        model.dat_rep >= date_from,
        model.dat_rep <= date_to,
        model.prod_uwi == WellStockHistExt.uwi,
        model.dat_rep == WellStockHistExt.status_date,
    )


def select_union_rates(
    date_from: date,
    date_to: date,
) -> Subquery:
    subq_prod = select_separate_well_rates(
        MonthlyProd, WellMode.PRODUCTION, date_from, date_to
    )
    subq_inj = select_separate_well_rates(
        MonthlyInj, WellMode.INJECTION, date_from, date_to
    )
    return union(subq_prod, subq_inj).subquery()


def select_well_rates(
    date_from: date,
    date_to: date,
) -> Select:
    subq = select_union_rates(date_from, date_to)
    return select(
        subq.c.field,
        subq.c.well_name,
        subq.c.cid,
        subq.c.cid_all,
        subq.c.dat_rep,
        func.sum(subq.c.oil_v).label('oil_v'),
        func.sum(subq.c.water_v).label('water_v'),
        func.sum(subq.c.water).label('water'),
        func.sum(subq.c.days).label('days'),
    ).group_by(
        subq.c.field,
        subq.c.well_name,
        subq.c.cid,
        subq.c.cid_all,
        subq.c.dat_rep,
    )
