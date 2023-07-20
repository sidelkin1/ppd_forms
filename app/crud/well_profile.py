from datetime import date

from sqlalchemy import delete, insert, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.crud.queryset.ofm.well_profile import select_well_profiles
from app.models.well_profile import WellProfile


class CRUDWellProfile(CRUDBase):

    async def refresh_local_database(
        self,
        date_from: date,
        date_to: date,
        local_session: AsyncSession,
        ofm_session: Session,
    ) -> None:
        ofm_data = await self.get_ofm_data(
            select_well_profiles(date_from, date_to), ofm_session
        )
        await local_session.execute(
            delete(WellProfile).where(
                tuple_(
                    WellProfile.uwi,
                    WellProfile.rec_date,
                ).in_([
                    (row.uwi, row.rec_date) for row in ofm_data
                ])
            )
        )
        await local_session.execute(
            insert(WellProfile),
            [row._mapping for row in ofm_data],
        )
        await local_session.commit()
        print('Done!')


crud_well_profile = CRUDWellProfile(WellProfile)
