from sqlalchemy import Date, Select, bindparam, func, or_, select

from app.infrastructure.db.models.ofm.reflected import DictG, Pressure, WellHdr


def select_tank_bhp() -> Select:
    return select(
        DictG.description.label("Field"),
        WellHdr.well_name.label("Well"),
        Pressure.cid.label("Reservoir"),
        func.trunc(Pressure.test_date, "month").cast(Date).label("Date"),
        Pressure.source.label("Source_bhp"),
        (
            func.coalesce(Pressure.owc_bhp_incl, Pressure.owc_bhp_arm) * 10.2
        ).label("Pbhp"),
    ).where(
        Pressure.field == DictG.id,
        Pressure.uwi == WellHdr.uwi,
        or_(
            Pressure.owc_bhp_incl.is_not(None),
            Pressure.owc_bhp_arm.is_not(None),
        ),
        Pressure.source.in_(("OIS Gen", "Геолог УН")),
        (DictG.description + WellHdr.well_name + Pressure.cid).in_(
            bindparam("uids")
        ),
    )
