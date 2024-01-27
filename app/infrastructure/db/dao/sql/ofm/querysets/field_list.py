from sqlalchemy import select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import DictG


def select_fields() -> Select:
    return select(DictG.id, DictG.description.label("name")).where(
        DictG.grp == 1670, DictG.code.is_not(None)
    )
