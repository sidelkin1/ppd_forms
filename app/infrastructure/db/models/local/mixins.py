from datetime import date
from typing import Protocol

from sqlalchemy.orm import Mapped, declared_attr, synonym


class DateStampMixin(Protocol):
    @declared_attr
    def date_stamp(cls) -> Mapped[date]:
        raise NotImplementedError


def date_stamp_factory(date_stamp) -> type[DateStampMixin]:
    class DateStampMixin:
        @declared_attr
        def date_stamp(cls) -> Mapped[date]:
            return synonym(date_stamp)

    return DateStampMixin
