from sqlalchemy import bindparam, func, select, table, union
from sqlalchemy.sql.expression import CompoundSelect

from app.infrastructure.db.models.ofm.reflected import DictG


def select_reservoir_ids() -> CompoundSelect:
    return union(
        select(bindparam("reservoir_id").label("reservoir")).select_from(
            table("dual")
        ),
        select(DictG.id.label("reservoir")).where(
            DictG.mr == func.to_char(bindparam("reservoir_id"))
        ),
    )
