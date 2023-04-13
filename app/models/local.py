from sqlalchemy import (Column, Date, Float, Index, String, Text,
                        UniqueConstraint)

from app.core.local_db import Base


class MonthlyReport(Base):
    field = Column(String(50), nullable=False)
    well_name = Column(String(10), nullable=False)
    cid = Column(String(20), nullable=False)
    cid_all = Column(String(50), nullable=False)
    date_stamp = Column('dat_rep', Date, nullable=False)
    oil_v = Column(Float, nullable=False)
    water_v = Column(Float, nullable=False)
    water = Column(Float, nullable=False)
    days = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            field, well_name, cid, date_stamp,
            name='field-well_name-cid-date_stamp',
        ),
    )


class WellProfile(Base):
    field = Column(String(50), nullable=False)
    uwi = Column(String(10), nullable=False)
    well_name = Column(String(10), nullable=False)
    well_type = Column(String(50))
    date_stamp = Column('rec_date', Date, nullable=False)
    cid_all = Column(String(50), nullable=False)
    layer = Column(String(100))
    top = Column(Float, nullable=False)
    bottom = Column(Float, nullable=False)
    abstop = Column(Float)
    absbotm = Column(Float)
    diff_absorp = Column(Float)
    tot_absorp = Column(Float)
    liq_rate = Column(Float)
    remarks = Column(Text)

    __table_args__ = (
        Index('uwi-date_stamp', uwi, date_stamp),
    )
