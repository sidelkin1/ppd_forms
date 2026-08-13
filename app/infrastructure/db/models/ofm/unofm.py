from sqlalchemy import Column, String
from sqlalchemy.orm import column_property

from app.infrastructure.db.dao.sql.querysets.license import (
    select_cid_no_license,
    select_uniqueid_no_license,
)
from app.infrastructure.db.models.ofm.base import Base, Reflected


class Unofm(Base):
    __abstract__ = True


def setup_column_properties() -> None:
    """Add cid_no_license / uniqueid_no_license column_properties to all
    Unofm subclasses after OFM reflection is complete.

    Must be called after Reflected.prepare() — DictG columns must exist.
    """
    for cls in Unofm.__subclasses__():
        if hasattr(cls, "cid"):
            cls.cid_no_license = column_property(
                select_cid_no_license(cls.cid)
            )
        if hasattr(cls, "uniqueid"):
            cls.uniqueid_no_license = column_property(
                select_uniqueid_no_license(cls.uniqueid)
            )


class MonthlyProd(Reflected, Unofm):
    __tablename__ = "monthlyprod"
    __table_args__ = {"schema": "unofm"}


class MonthlyProdAlt(Reflected, Unofm):
    __tablename__ = "monthlyprod_alt"
    __table_args__ = {"schema": "unofm"}


class MonthlyInj(Reflected, Unofm):
    __tablename__ = "monthly_inj"
    __table_args__ = {"schema": "unofm"}


class MonthlyInjAlt(Reflected, Unofm):
    __tablename__ = "monthly_inj_alt"
    __table_args__ = {"schema": "unofm"}


class Reservoir(Reflected, Unofm):
    # https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    field = Column(String, primary_key=True)
    cid = Column(String, primary_key=True)

    __tablename__ = "reservoir"
    __table_args__ = {"schema": "unofm"}


class HeaderId(Reflected, Unofm):
    __tablename__ = "headerid"
    __table_args__ = {"schema": "unofm"}


class LayersPty(Reflected, Unofm):
    __tablename__ = "layers_pty"
    __table_args__ = {"schema": "unofm"}


class Perf(Reflected, Unofm):
    # https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    uwi = Column(String, primary_key=True)
    date_op = Column(String, primary_key=True)

    __tablename__ = "perf"
    __table_args__ = {"schema": "unofm"}


class PerfAlt(Reflected, Unofm):
    # https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    uwi = Column(String, primary_key=True)
    date_op = Column(String, primary_key=True)

    __tablename__ = "perf_alt"
    __table_args__ = {"schema": "unofm"}


class Pressure(Reflected, Unofm):
    __tablename__ = "pressure"
    __table_args__ = {"schema": "unofm"}


class Notes(Reflected, Unofm):
    __tablename__ = "notes"
    __table_args__ = {"schema": "unofm"}
