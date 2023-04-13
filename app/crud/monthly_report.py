from datetime import date
from enum import Enum

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import delete, func, insert, literal_column, select, union
from sqlalchemy.dialects.sqlite import insert as upsert
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import ColumnClause, Select, Subquery

from app.core.ofm_db import Base
from app.crud.base import CRUDLocalBase, CRUDOfmBase
from app.models.local import MonthlyReport
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


class CRUDOfmRead(CRUDOfmBase):

    def select_well_rates(
        self,
        model: type[Base],
        wmode: WellMode,
        date_from: date,
        date_to: date,
    ) -> Select:
        return select(
            self.select_description(model, 'field').label('field'),
            self.select_well_name(model, 'prod_uwi').label('well_name'),
            model.cid,
            self.select_cids().label('cid_all'),
            model.dat_rep,
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

    def get_union_rates(
        self,
        date_from: date,
        date_to: date,
    ) -> Subquery:
        subq_prod = self.select_well_rates(
            MonthlyProd, WellMode.PRODUCTION, date_from, date_to
        )
        subq_inj = self.select_well_rates(
            MonthlyInj, WellMode.INJECTION, date_from, date_to
        )
        return union(subq_prod, subq_inj).subquery()

    def get_ofm_data(
        self,
        date_from: date,
        date_to: date,
        session: Session,
    ) -> list[Row]:
        subq = self.get_union_rates(date_from, date_to)
        stmt = select(
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
        return session.execute(stmt).all()


class CRUDMonthlyReport(CRUDLocalBase):

    async def reload_local_database(
        self,
        date_from: date,
        date_to: date,
        local_session: AsyncSession,
        ofm_session: Session,
    ) -> None:
        ofm_data = await run_in_threadpool(
            self.ofm_crud.get_ofm_data, date_from, date_to, ofm_session
        )
        await local_session.execute(delete(self.model))
        await local_session.execute(
            insert(self.model),
            [row._mapping for row in ofm_data],
        )
        await local_session.commit()
        print('Done!')

    async def refresh_local_database(
        self,
        date_from: date,
        date_to: date,
        local_session: AsyncSession,
        ofm_session: Session,
    ) -> None:
        ofm_data = await run_in_threadpool(
            self.ofm_crud.get_ofm_data, date_from, date_to, ofm_session
        )
        stmt = upsert(self.model)
        await local_session.execute(
            stmt.on_conflict_do_update(
                index_elements=self.model.get_constraint_by_name(
                    'field-well_name-cid-date_stamp'
                ),
                set_=dict(
                    cid_all=stmt.excluded.cid_all,
                    oil_v=stmt.excluded.oil_v,
                    water_v=stmt.excluded.water_v,
                    water=stmt.excluded.water,
                    days=stmt.excluded.days,
                )
            ),
            [row._mapping for row in ofm_data],
        )
        await local_session.commit()
        print('Done!')


crud_monthly_report = CRUDMonthlyReport(MonthlyReport, CRUDOfmRead())
