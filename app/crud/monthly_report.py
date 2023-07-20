from datetime import date

from sqlalchemy import delete, insert
from sqlalchemy.dialects.sqlite import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.crud.queryset.ofm.well_report import select_well_rates
from app.models.monthly_report import MonthlyReport


class CRUDMonthlyReport(CRUDBase):

    async def reload_local_database(
        self,
        date_from: date,
        date_to: date,
        local_session: AsyncSession,
        ofm_session: Session,
    ) -> None:
        ofm_data = await self.get_ofm_data(
            select_well_rates(date_from, date_to), ofm_session
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
        ofm_data = await self.get_ofm_data(
            select_well_rates(date_from, date_to), ofm_session
        )
        stmt = upsert(self.model)
        await local_session.execute(
            stmt.on_conflict_do_update(
                index_elements=self.model.get_constraint_by_name(
                    'field-well_name-cid-dat_rep'
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


crud_monthly_report = CRUDMonthlyReport(MonthlyReport)
