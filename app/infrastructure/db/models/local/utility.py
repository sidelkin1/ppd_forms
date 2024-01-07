from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config.settings import get_settings
from app.infrastructure.db.models.local.base import Base

settings = get_settings()  # FIXME avoid global variable


class BaseReplace:
    group: Mapped[str] = mapped_column(String(20))
    replace: Mapped[str] = mapped_column(String(100))
    order: Mapped[int | None]

    __table_args__ = {"schema": settings.util_table_schema}


class BasePattern:
    pattern: Mapped[str] = mapped_column(String(150))


class FieldReplace(BaseReplace, BasePattern, Base):
    pass


class ReservoirReplace(BaseReplace, BasePattern, Base):
    pass


class LayerReplace(BaseReplace, Base):
    pass
