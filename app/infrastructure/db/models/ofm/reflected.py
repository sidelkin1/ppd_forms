from sqlalchemy import Column, Integer, String

from app.infrastructure.db.models.ofm.base import Base, Reflected


class MonthlyProd(Reflected, Base):
    __tablename__ = "monthlyprod"
    __table_args__ = {"schema": "unofm"}


class MonthlyInj(Reflected, Base):
    __tablename__ = "monthly_inj"
    __table_args__ = {"schema": "unofm"}


class DictG(Reflected, Base):
    __tablename__ = "dict_g"
    __table_args__ = {"schema": "codes"}


class GeophysStAbsorp(Reflected, Base):
    __tablename__ = "geophys_st_absorp"
    __table_args__ = {"schema": "udmurtneft_n"}


class GeophysSt(Reflected, Base):
    __tablename__ = "geophys_st"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellHdr(Reflected, Base):
    __tablename__ = "well_hdr"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellStockHistExt(Reflected, Base):
    __tablename__ = "well_stock_hist_ext"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellLogResultSublayers(Reflected, Base):
    __tablename__ = "well_log_result_sublayers"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellLogResultLayers(Reflected, Base):
    __tablename__ = "well_log_result_layers"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellOrapMd(Reflected, Base):
    # https://docs.sqlalchemy.org/en/14/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key # noqa
    uwi = Column(String, primary_key=True)
    reservoir_id = Column(Integer, primary_key=True)

    __tablename__ = "well_orap_md"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellPerforations(Reflected, Base):
    __tablename__ = "well_perforations"
    __table_args__ = {"schema": "udmurtneft_n"}
