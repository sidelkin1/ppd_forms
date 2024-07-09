from sqlalchemy import (
    CompoundSelect,
    Date,
    Select,
    and_,
    bindparam,
    literal_column,
    select,
    union,
)
from sqlalchemy.orm import aliased

from app.infrastructure.db.models.ofm.reflected import (
    DictG,
    HeaderId,
    MonthlyInj,
    MonthlyProd,
    Reservoir,
    WellHdr,
)


def _select_production_rates() -> Select:
    dictg_alias = aliased(DictG)
    return (
        select(
            DictG.description.label("field"),
            dictg_alias.description.label("district"),
            MonthlyProd.cid.label("reservoir"),
            Reservoir.oil_compressibility.label("oil_fvf"),
            literal_column("'prod'").label("type"),
            WellHdr.well_name.label("well"),
            MonthlyProd.dat_rep.cast(Date).label("date"),
            MonthlyProd.water_v.label("water"),
            MonthlyProd.oil_v.label("oil"),
            MonthlyProd.days.label("days"),
        )
        .outerjoin(DictG, DictG.id == MonthlyProd.field)
        .outerjoin(WellHdr, WellHdr.uwi == MonthlyProd.uwi)
        .outerjoin(
            HeaderId,
            and_(
                HeaderId.uwi == MonthlyProd.uwi,
                HeaderId.cid == MonthlyProd.cid,
            ),
        )
        .outerjoin(
            Reservoir,
            and_(
                Reservoir.field == MonthlyProd.field,
                Reservoir.cid == MonthlyProd.cid,
                Reservoir.district_id == HeaderId.district_id,
            ),
        )
        .outerjoin(dictg_alias, dictg_alias.id == HeaderId.district_id)
        .where(MonthlyProd.dat_rep == bindparam("on_date"))
    )


def _select_injection_rates() -> Select:
    dictg_alias = aliased(DictG)
    return (
        select(
            DictG.description.label("field"),
            dictg_alias.description.label("district"),
            MonthlyInj.cid.label("reservoir"),
            Reservoir.oil_compressibility.label("oil_fvf"),
            literal_column("'inj'").label("type"),
            WellHdr.well_name.label("well"),
            MonthlyInj.dat_rep.cast(Date).label("date"),
            MonthlyInj.water.label("water"),
            literal_column("0").label("oil_v"),
            MonthlyInj.days.label("days"),
        )
        .outerjoin(DictG, DictG.id == MonthlyInj.field)
        .outerjoin(WellHdr, WellHdr.uwi == MonthlyInj.uwi)
        .outerjoin(
            HeaderId,
            and_(
                HeaderId.uwi == MonthlyInj.uwi,
                HeaderId.cid == MonthlyInj.cid,
            ),
        )
        .outerjoin(
            Reservoir,
            and_(
                Reservoir.field == MonthlyInj.field,
                Reservoir.cid == MonthlyInj.cid,
                Reservoir.district_id == HeaderId.district_id,
            ),
        )
        .outerjoin(dictg_alias, dictg_alias.id == HeaderId.district_id)
        .where(MonthlyInj.dat_rep == bindparam("on_date"))
    )


def select_compensation_rates() -> CompoundSelect:
    return union(_select_production_rates(), _select_injection_rates())
