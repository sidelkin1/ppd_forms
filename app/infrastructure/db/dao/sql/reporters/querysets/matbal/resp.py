from sqlalchemy import (
    Date,
    Select,
    bindparam,
    func,
    literal_column,
    select,
    union_all,
)

from app.infrastructure.db.models.ofm.codes import DictG
from app.infrastructure.db.models.ofm.udmurtneft_n import (
    TmpWellNgOis2,
    TmpWellOpOis2,
    WellHdr,
)


def _select_reservoirs() -> Select:
    return select(func.lower(DictG.description).label("reservoir")).where(
        func.nvl(DictG.mr, func.to_char(DictG.id)).in_(
            bindparam("reservoir_ids")
        )
    )


def _select_field_uwis() -> Select:
    return select(func.coalesce(WellHdr.parent_uwi, WellHdr.uwi)).where(
        WellHdr.field == bindparam("field_id")
    )


def _select_well_uwis() -> Select:
    return _select_field_uwis().where(
        WellHdr.well_name.in_(bindparam("wells"))
    )


def _select_tr_oil(uwis: Select) -> Select:
    return (
        select(
            func.min(TmpWellOpOis2.official_date).label("date"),
            func.avg(TmpWellOpOis2.shut_pressure).label("resp"),
            func.avg(TmpWellOpOis2.init_shut_pressure).label("init_resp"),
            func.avg(TmpWellOpOis2.oil_compressibility).label("oil_fvf"),
        )
        .where(
            TmpWellOpOis2.uwi.in_(uwis),
            func.lower(TmpWellOpOis2.layer_id).in_(_select_reservoirs()),
        )
        .group_by(TmpWellOpOis2.uwi, TmpWellOpOis2.official_date)
    )


def _select_tr_inj(uwis: Select) -> Select:
    return (
        select(
            func.min(TmpWellNgOis2.official_date).label("date"),
            func.avg(TmpWellNgOis2.layer_shut_pressure).label("resp"),
            literal_column("NULL").label("init_resp"),
            literal_column("NULL").label("oil_fvf"),
        )
        .where(
            TmpWellNgOis2.uwi.in_(uwis),
            func.lower(TmpWellNgOis2.layer_id).in_(_select_reservoirs()),
        )
        .group_by(TmpWellNgOis2.uwi, TmpWellNgOis2.official_date)
    )


def select_field_resp() -> Select:
    uwis = _select_field_uwis()
    subq = union_all(_select_tr_oil(uwis), _select_tr_inj(uwis))
    return (
        select(
            func.min(subq.c.date).cast(Date).label("date"),
            func.avg(subq.c.resp).label("Pres"),
            func.avg(subq.c.init_resp).label("Pi"),
            func.avg(subq.c.oil_fvf).label("Boi"),
        )
        .group_by(subq.c.date)
        .order_by(subq.c.date)
    )


def select_well_resp() -> Select:
    uwis = _select_well_uwis()
    subq = union_all(_select_tr_oil(uwis), _select_tr_inj(uwis))
    return (
        select(
            func.min(subq.c.date).cast(Date).label("date"),
            func.avg(subq.c.resp).label("Pres"),
            func.avg(subq.c.init_resp).label("Pi"),
            func.avg(subq.c.oil_fvf).label("Boi"),
        )
        .group_by(subq.c.date)
        .order_by(subq.c.date)
    )
