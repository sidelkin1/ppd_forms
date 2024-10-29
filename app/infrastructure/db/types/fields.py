from app.infrastructure.db.mappers import field_mapper
from app.infrastructure.db.types.base import BaseType


class FieldType(BaseType):
    def process_bind_param(self, value, dialect):
        return field_mapper[value]
