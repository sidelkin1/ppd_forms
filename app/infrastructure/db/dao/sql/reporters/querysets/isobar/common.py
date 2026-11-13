from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import ColumnElement

from app.infrastructure.db.models.ofm.codes import DictG


def base_reservoir_id() -> ColumnElement[int]:
    """id базового объекта разработки для строки справочника.

    У «ИЖВ»-объектов ``mr`` ссылается на базовый объект (например,
    «Визейский (ИЖВ 01973 НЭ)» → базовый «визейский»). Резолв нужен,
    чтобы смена объекта на ИЖВ и обратно не выглядела сменой ствола.

    Ссылка сравнивается с ``to_char(id)`` в строковом домене, а числовой
    ``id`` берётся из найденной строки справочника: нечисловой ``mr``
    (``НЯ``, ``УГЛ``, ``БГЛ``...) не приводит к ``ORA-01722``.
    """
    base = aliased(DictG)
    reference = func.decode(DictG.mr, None, func.to_char(DictG.id), DictG.mr)
    return (
        select(base.id)
        .where(func.to_char(base.id) == reference)
        .scalar_subquery()
    )


def cid_column() -> ColumnElement[str]:
    """Объект разработки в домене локальной БД.

    Совпадает с ``cid`` фонда и ``welltest.reservoir``: у объектов с
    заполненным ``mr`` (ИЖВ) берётся ``sdes`` базового объекта, поэтому
    просто ``DictG.sdes`` использовать нельзя — получатся «Вз(01973)»
    вместо «Вз».
    """
    return func.replace(
        func.udmurtneft_n.dg_sdes(
            func.decode(DictG.mr, None, DictG.id, DictG.mr)
        ),
        "(Руд)",
        "",
    )
