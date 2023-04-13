from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ScalarSelect

from app.core.local_db import Base as LocalBase
from app.core.ofm_db import Base as OFMBase
from app.models.ofm import DictG, WellHdr, WellStockHistExt


class CRUDOfmBase:

    def select_description(
        self,
        model: type[OFMBase],
        field_id: str,
        field_descr: str = 'description',
    ) -> ScalarSelect:
        return select(
            getattr(DictG, field_descr)
        ).where(
            getattr(model, field_id) == DictG.id
        ).scalar_subquery().correlate(model)

    def select_well_name(
        self,
        model: type[OFMBase],
        field_id: str,
    ) -> ScalarSelect:
        return select(
            WellHdr.well_name
        ).where(
            getattr(model, field_id) == WellHdr.uwi
        ).scalar_subquery().correlate(model)

    def select_cids(self) -> ScalarSelect:
        subq_cid1 = self.select_description(
            WellStockHistExt, 'ora1', field_descr='sdes'
        )
        subq_cid2 = self.select_description(
            WellStockHistExt, 'ora2', field_descr='sdes'
        )
        # sourcery skip: use-fstring-for-concatenation
        return func.decode(
            subq_cid2, None, subq_cid1,
            subq_cid1 + ' ' + subq_cid2,
        )


class CRUDLocalBase:

    def __init__(self, model: type[LocalBase], ofm_crud: CRUDOfmBase):
        self.model = model
        self.ofm_crud = ofm_crud

    async def get_min_max_dates(
        self,
        session: AsyncSession,
    ) -> tuple[date, date]:
        result = await session.execute(
            select(
                func.min(self.model.date_stamp),
                func.max(self.model.date_stamp),
            )
        )
        return result.one()
