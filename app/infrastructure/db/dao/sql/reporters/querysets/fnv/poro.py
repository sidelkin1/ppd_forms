from sqlalchemy import Select, and_, bindparam, func, select
from sqlalchemy.orm import MappedColumn

from app.infrastructure.db.models.ofm.reflected import HeaderId, LayersPty


def _select_poro(porosity: MappedColumn) -> Select:
    return (
        select(
            LayersPty.layer_name,
            LayersPty.cid,
            HeaderId.xcoord,
            HeaderId.ycoord,
            func.min(LayersPty.top).label("ktop"),
            func.max(LayersPty.botm).label("kbot"),
            (
                func.sum(LayersPty.h_eff * porosity)
                / func.sum(LayersPty.h_eff)
            ).label("poro"),
            func.avg(LayersPty.kn).label("knas"),
            func.sum(LayersPty.h_eff).label("h"),
        )
        .outerjoin(
            HeaderId,
            and_(LayersPty.uwi == HeaderId.uwi, LayersPty.cid == HeaderId.cid),
        )
        .where(
            LayersPty.uwi == bindparam("uwi"),
            LayersPty.h_eff.is_not(None),
            LayersPty.h_eff > 0,
            porosity.is_not(None),
            LayersPty.numv.in_((1, 3)),
        )
        .group_by(
            LayersPty.layer_name,
            LayersPty.cid,
            HeaderId.xcoord,
            HeaderId.ycoord,
        )
        .order_by("ktop")
    )


def select_poro() -> Select:
    return _select_poro(LayersPty.porosity)


def select_poro_alt() -> Select:
    return _select_poro(LayersPty.porosity_alt)
