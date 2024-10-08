from app.infrastructure.db.mappers import multi_well_mapper, well_mapper
from app.infrastructure.db.types.base import BaseType


class WellType(BaseType):
    def process_bind_param(self, value, dialect):
        return well_mapper[value]


class MultiWellType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_well_mapper[value]
