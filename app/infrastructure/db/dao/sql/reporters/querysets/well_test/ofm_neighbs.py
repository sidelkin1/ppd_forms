from sqlalchemy import and_, bindparam, func, select
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.ofm.reflected import DictG, HeaderId, WellHdr


def _select_well_coords() -> Subquery:
    return (
        select(
            HeaderId.field,
            HeaderId.cid,
            HeaderId.xcoord,
            HeaderId.ycoord,
        )
        .join(WellHdr, WellHdr.uwi == HeaderId.uwi)
        .join(DictG, DictG.id == HeaderId.field)
        .where(
            DictG.description == bindparam("field"),
            WellHdr.well_name == bindparam("well"),
            HeaderId.cid.in_(bindparam("reservoirs")),
        )
    ).subquery()


def select_ofm_neighbs() -> Select:
    subq = _select_well_coords()
    radius = func.sqrt(
        func.power(HeaderId.xcoord - subq.c.xcoord, 2)
        + func.power(HeaderId.ycoord - subq.c.ycoord, 2)
    )
    return (
        select(
            DictG.description.label("field"),
            WellHdr.well_name.label("well"),
            HeaderId.cid.label("reservoir"),
            func.round(radius, 1).label("distance"),
        )
        .join(WellHdr, WellHdr.uwi == HeaderId.uwi)
        .join(DictG, DictG.id == HeaderId.field)
        .join(
            subq,
            and_(
                subq.c.field == HeaderId.field,
                subq.c.cid == HeaderId.cid,
            ),
        )
        .where(
            radius <= bindparam("radius"),
            WellHdr.well_name != bindparam("well"),
        )
        .order_by(HeaderId.cid)
    )
