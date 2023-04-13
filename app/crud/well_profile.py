from datetime import date

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import (between, delete, distinct, func, insert, or_, select,
                        tuple_)
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import ColumnElement, ScalarSelect
from sqlalchemy.sql.functions import Function

from app.core.ofm_db import Base
from app.crud.base import CRUDLocalBase, CRUDOfmBase
from app.models.local import WellProfile
from app.models.ofm import (GeophysSt, GeophysStAbsorp, WellHdr,
                            WellLogResultLayers, WellLogResultSublayers,
                            WellOrapMd, WellPerforations, WellStockHistExt)


class CRUDOfmRead(CRUDOfmBase):

    def get_db_func(self, schema: str, name: str) -> Function:
        return getattr(getattr(func, schema), name)

    def get_str_sum(
        self,
        model: type[Base],
        schema: str,
        func_name: str,
        field: str,
    ) -> ColumnElement:
        db_func = self.get_db_func(schema, func_name)
        return func.ofm.str_sum(distinct(db_func(getattr(model, field))))

    def check_interval_intersections(self, model: type[Base]) -> ColumnElement:
        return or_(
            or_(
                between(model.top,
                        GeophysStAbsorp.top,
                        GeophysStAbsorp.bottom),
                between(model.base,
                        GeophysStAbsorp.top,
                        GeophysStAbsorp.bottom),
            ),
            or_(
                between(GeophysStAbsorp.top,
                        model.top,
                        model.base),
                between(GeophysStAbsorp.bottom,
                        model.top,
                        model.base),
            ),
        )

    def calc_abs_depth(self, depth: str) -> ColumnElement:
        md = getattr(GeophysStAbsorp, depth)
        tvd = func.udmurtneft_n.z_get_tvd(GeophysSt.uwi, md)
        return func.round(WellHdr.elevation - tvd, 1)

    def remove_well_branch(self) -> ColumnElement:
        return func.decode(
            func.instr(GeophysSt.uwi, 'B'), 0,
            GeophysSt.uwi,
            WellHdr.parent_uwi,
        )

    def select_layer_perf(
        self,
        model: type[Base],
        schema: str,
        func_name: str,
        field: str,
        *where_args,
    ) -> ScalarSelect:
        return select(
            self.get_str_sum(model, schema, func_name, field)
        ).where(
            self.check_interval_intersections(model),
            *where_args,
        ).scalar_subquery().correlate(GeophysSt, GeophysStAbsorp)

    def select_layers(self) -> ScalarSelect:
        subq_lr1 = self.select_layer_perf(
            WellOrapMd, 'udmurtneft_n', 'dg_sdes', 'reservoir_id',
            WellOrapMd.uwi == GeophysSt.uwi,
        )
        subq_lr2 = self.select_layer_perf(
            WellLogResultLayers, 'udmurtneft_n', 'dg_des', 'layer_id',
            WellLogResultSublayers.uwi == GeophysSt.uwi,
            WellLogResultSublayers.uwi == WellLogResultLayers.uwi,
            WellLogResultSublayers.layer_id == WellLogResultLayers.layer_id,
            WellLogResultSublayers.source == WellLogResultLayers.source,
            WellLogResultSublayers.interpreter.in_((1, 3)),
        )
        # sourcery skip: use-fstring-for-concatenation
        return subq_lr1 + ': ' + subq_lr2

    def get_ofm_data(
        self,
        date_from: date,
        date_to: date,
        session: Session,
    ) -> list[Row]:
        subq_lr = self.select_layers()
        subq_perf = self.select_layer_perf(
            WellPerforations, 'udmurtneft_n', 'dg_sdes', 'layer_id',
            WellPerforations.uwi == GeophysSt.uwi,
        )
        stmt = select(
            self.select_description(WellHdr, 'field').label('field'),
            GeophysSt.uwi,
            WellHdr.well_name,
            self.select_description(
                GeophysSt, 'prod_class'
            ).label('well_type'),
            GeophysSt.rec_date,
            self.select_cids().label('cid_all'),
            func.decode(subq_lr, ': ', subq_perf, subq_lr).label('layer'),
            GeophysStAbsorp.top,
            GeophysStAbsorp.bottom,
            self.calc_abs_depth('top').label('abstop'),
            self.calc_abs_depth('bottom').label('absbotm'),
            GeophysStAbsorp.diff_absorp,
            GeophysSt.tot_absorp,
            GeophysSt.liq_rate,
            GeophysStAbsorp.remarks,
        ).select_from(
            GeophysStAbsorp,
            GeophysSt,
            WellHdr,
            WellStockHistExt,
        ).where(
            GeophysStAbsorp.id == GeophysSt.id,
            WellHdr.uwi == GeophysSt.uwi,
            (
                WellStockHistExt.status_date
                == func.trunc(GeophysSt.rec_date, 'mm')
            ),
            self.remove_well_branch() == WellStockHistExt.uwi,
            GeophysSt.rec_date >= date_from,
            GeophysSt.rec_date <= date_to,
        )
        return session.execute(stmt).all()


class CRUDWellProfile(CRUDLocalBase):

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
        await local_session.execute(
            delete(WellProfile).where(
                tuple_(
                    WellProfile.uwi,
                    WellProfile.date_stamp
                ).in_(
                    [(row.uwi, row.rec_date) for row in ofm_data],
                )
            )
        )
        await local_session.execute(
            insert(WellProfile),
            [row._mapping for row in ofm_data],
        )
        await local_session.commit()
        print('Done!')


crud_well_profile = CRUDWellProfile(WellProfile, CRUDOfmRead())
