from app.infrastructure.db.models.ofm.base import Base, Reflected


class DictG(Reflected, Base):
    __tablename__ = "dict_g"
    __table_args__ = {"schema": "codes"}
