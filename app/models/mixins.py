from datetime import date
from typing import Any

from sqlalchemy.orm import Mapped, declared_attr, synonym


def date_stamp_factory(attr_name: str) -> Any:
    dict_ = dict(
        date_stamp=declared_attr(lambda _: synonym(attr_name)),
        __annotations__={attr_name: Mapped[date]},
    )
    return type('DateStampMixin', (), dict_)
