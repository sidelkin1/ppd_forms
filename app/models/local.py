from datetime import date
from typing import Optional

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.core.local_db import Base


class MonthlyReport(Base):
    field: Mapped[str] = mapped_column(String(50))
    well_name: Mapped[str] = mapped_column(String(10))
    cid: Mapped[str] = mapped_column(String(20))
    cid_all: Mapped[str] = mapped_column(String(50))
    dat_rep: Mapped[date]
    oil_v: Mapped[float]
    water_v: Mapped[float]
    water: Mapped[float]
    days: Mapped[float]

    @declared_attr.directive
    def date_stamp(cls) -> Mapped[date]:
        return cls.dat_rep

    __table_args__ = (
        UniqueConstraint(
            'field', 'well_name', 'cid', 'dat_rep',
            name='field-well_name-cid-dat_rep',
        ),
    )


class WellProfile(Base):
    field = mapped_column(String(50))
    uwi = mapped_column(String(10))
    well_name = mapped_column(String(10))
    well_type = mapped_column(String(50))
    rec_date: Mapped[date]
    cid_all = mapped_column(String(50))
    layer = mapped_column(String(100))
    top: Mapped[float]
    bottom: Mapped[float]
    abstop: Mapped[Optional[float]]
    absbotm: Mapped[Optional[float]]
    diff_absorp: Mapped[Optional[float]]
    tot_absorp: Mapped[Optional[float]]
    liq_rate: Mapped[Optional[float]]
    remarks: Mapped[Optional[str]]

    @declared_attr.directive
    def date_stamp(cls) -> Mapped[date]:
        return cls.rec_date

    __table_args__ = (
        Index('uwi-rec_date', 'uwi', 'rec_date'),
    )
