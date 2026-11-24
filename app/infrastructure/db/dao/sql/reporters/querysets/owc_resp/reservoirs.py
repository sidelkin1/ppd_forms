from sqlalchemy import bindparam, func, select, table, union
from sqlalchemy.sql.expression import CompoundSelect

from app.infrastructure.db.models.ofm.codes import DictG


def select_reservoir_ids() -> CompoundSelect:
    return union(
        select(bindparam("reservoir_id").label("reservoir")).select_from(
            table("dual")
        ),
        select(DictG.id.label("reservoir")).where(
            DictG.mr == func.to_char(bindparam("reservoir_id"))
        ),
    )


def select_reservoir_names() -> CompoundSelect:
    """Имена объекта в нижнем регистре: базовый id и его `mr`-псевдоним.

    Техрежим хранит пласт текстом в кодировке месторождения, поэтому
    сопоставление идёт не по числовому id, а по описанию из словаря.
    """
    return union(
        select(func.lower(DictG.description).label("reservoir")).where(
            DictG.id == bindparam("reservoir_id")
        ),
        select(func.lower(DictG.description).label("reservoir")).where(
            DictG.mr == func.to_char(bindparam("reservoir_id"))
        ),
    )
