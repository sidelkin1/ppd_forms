from sqlalchemy import Select, bindparam, select

from app.infrastructure.db.models.ofm.reflected import LayersPty


def select_layers() -> Select:
    return (
        select(LayersPty.cid, LayersPty.layer_name)
        .where(
            LayersPty.field == bindparam("field_id"),
            LayersPty.numv.in_((1, 3)),
        )
        .distinct()
    )
