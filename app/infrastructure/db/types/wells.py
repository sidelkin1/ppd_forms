from app.infrastructure.db.mappers import (
    multi_well_mapper,
    multi_well_no_branch_mapper,
    well_mapper,
    well_no_branch_mapper,
)
from app.infrastructure.db.types.base import BaseType


class WellType(BaseType):
    def process_bind_param(self, value, dialect):
        return well_mapper[value]


class WellNoBranchType(BaseType):
    def process_bind_param(self, value, dialect):
        return well_no_branch_mapper[value]


class MultiWellType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_well_mapper[value]


class MultiWellNoBranchType(BaseType):
    def process_bind_param(self, value, dialect):
        return multi_well_no_branch_mapper[value]
