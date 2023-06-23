from datetime import date
from functools import reduce

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import ScalarSelect

from app.core.local_db import Base as LocalBase
from app.core.ofm_db import Base as OFMBase
from app.models.ofm import DictG, WellHdr, WellStockHistExt


class CRUDOfmBase:

    MAX_NUMBER_OF_ORA = 3

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
        subqs = [self.select_description(
            WellStockHistExt, f'ora{num}', field_descr='sdes'
        ) for num in range(1, self.MAX_NUMBER_OF_ORA + 1)]
        # sourcery skip: use-fstring-for-concatenation
        return reduce(
            lambda result, subq: func.decode(
                subq, None, result,
                subq + ' ' + result,
            ),
            subqs,
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
