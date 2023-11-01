from sqlalchemy import select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.local import Neighborhood


def select_neighborhood() -> Select:
    return select(
        Neighborhood.field,
        Neighborhood.reservoir,
        Neighborhood.well,
        Neighborhood.neighbs,
    )
