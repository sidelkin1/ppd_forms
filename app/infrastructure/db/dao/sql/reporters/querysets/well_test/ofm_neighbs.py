from sqlalchemy import and_, bindparam, func, select
from sqlalchemy.sql.expression import Select, Subquery

from app.infrastructure.db.models.ofm.reflected import DictG, HeaderId, WellHdr


def _select_well_coords() -> Subquery:
    subq = (
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
            (
                func.regexp_replace(WellHdr.well_name, r"B\d+$")
                == bindparam("well")
            ),
            HeaderId.cid.in_(bindparam("reservoirs")),
        )
    ).subquery()
    return (
        select(
            subq.c.field,
            subq.c.cid,
            func.avg(subq.c.xcoord).label("xcoord"),
            func.avg(subq.c.ycoord).label("ycoord"),
        )
        .group_by(subq.c.field, subq.c.cid)
        .subquery()
    )


def _select_well_neighbs() -> Subquery:
    subq = _select_well_coords()
    distance = func.sqrt(
        func.power(HeaderId.xcoord - subq.c.xcoord, 2)
        + func.power(HeaderId.ycoord - subq.c.ycoord, 2)
    )
    well_no_branch = func.regexp_replace(WellHdr.well_name, r"B\d+$")
    return (
        select(
            DictG.description.label("field"),
            well_no_branch.label("well"),
            HeaderId.cid.label("reservoir"),
            func.round(distance, 1).label("distance"),
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
            distance <= bindparam("radius"),
            well_no_branch != bindparam("well"),
        )
    ).subquery()


def select_ofm_neighbs() -> Select:
    subq = _select_well_neighbs()
    return select(
        subq.c.field,
        subq.c.well,
        subq.c.reservoir,
        func.avg(subq.c.distance).label("distance"),
    ).group_by(
        subq.c.field,
        subq.c.well,
        subq.c.reservoir,
    )
