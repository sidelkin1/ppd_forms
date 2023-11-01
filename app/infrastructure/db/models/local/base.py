from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)
from sqlalchemy.schema import Constraint

convention: dict[str, str] = {
    "ix": "ix__%(column_0_label)s",
    "uq": "uq__%(table_name)s__%(column_0_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "pk__%(table_name)s",
}
meta = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = meta

    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}"

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def get_constraint_by_name(cls, name: str) -> Constraint:
        return next(
            (
                constraint
                for constraint in cls.__table__.constraints
                if constraint.name == name
            )
        )
