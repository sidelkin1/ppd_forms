from sqlalchemy import Select, and_, bindparam, func, select

from app.infrastructure.db.models.ofm.reflected import HeaderId, LayersPty


def select_poro() -> Select:
    return (
        select(
            LayersPty.layer_name,
            LayersPty.cid,
            HeaderId.xcoord,
            HeaderId.ycoord,
            func.min(LayersPty.top).label("ktop"),
            func.max(LayersPty.botm).label("kbot"),
            (
                func.sum(LayersPty.h_eff * LayersPty.porosity)
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
            LayersPty.porosity.is_not(None),
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
