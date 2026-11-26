from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import ColumnElement, Select

from app.infrastructure.db.models.ofm.codes import DictG


def select_field_codes() -> Select:
    """Коды месторождений по названиям из справочника."""
    return select(func.to_char(DictG.id)).where(
        DictG.description.in_(bindparam("fields", expanding=True))
    )


def select_reservoir_layer_ids() -> Select:
    """Идентификаторы объектов разработки, включая объекты ИЖВ."""
    base = aliased(DictG)
    mapped = aliased(DictG)
    base_ids = select(func.to_char(base.id)).where(
        func.replace(base.sdes, "(Руд)", "").in_(
            bindparam("cids", expanding=True)
        )
    )
    return select(mapped.id).where(
        func.decode(mapped.mr, None, func.to_char(mapped.id), mapped.mr).in_(
            base_ids
        )
    )


def cid_column() -> ColumnElement[str]:
    """Объект разработки в домене локальной БД."""
    return func.replace(
        func.udmurtneft_n.dg_sdes(
            func.decode(DictG.mr, None, DictG.id, DictG.mr)
        ),
        "(Руд)",
        "",
    )
