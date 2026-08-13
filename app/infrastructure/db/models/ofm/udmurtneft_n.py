from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import synonym

from app.infrastructure.db.models.ofm.base import Base, Reflected


class GeophysStAbsorp(Reflected, Base):
    __tablename__ = "geophys_st_absorp"
    __table_args__ = {"schema": "udmurtneft_n"}


class GeophysSt(Reflected, Base):
    __tablename__ = "geophys_st"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellHdr(Reflected, Base):
    __tablename__ = "well_hdr"
    __table_args__ = {"schema": "udmurtneft_n"}

    class_ = synonym("class")


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
    # https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key
    uwi = Column(String, primary_key=True)
    reservoir_id = Column(Integer, primary_key=True)

    __tablename__ = "well_orap_md"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellPerforations(Reflected, Base):
    __tablename__ = "well_perforations"
    __table_args__ = {"schema": "udmurtneft_n"}


class ResPty(Reflected, Base):
    __tablename__ = "res_pty"
    __table_args__ = {"schema": "udmurtneft_n"}


class Reservoir2(Reflected, Base):
    __tablename__ = "reservoir2"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellMonthHist(Reflected, Base):
    __tablename__ = "well_month_hist"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellDirSrvyPts(Reflected, Base):
    __tablename__ = "well_dir_srvy_pts"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellStockHist(Reflected, Base):
    __tablename__ = "well_stock_hist"
    __table_args__ = {"schema": "udmurtneft_n"}


class WellMonthHistPty(Reflected, Base):
    __tablename__ = "well_month_hist_pty"
    __table_args__ = {"schema": "udmurtneft_n"}
