from sqlalchemy import Date, Select, bindparam, func, or_, select

from app.infrastructure.db.models.ofm.reflected import DictG, Pressure, WellHdr


def select_tank_pressures() -> Select:
    return select(
        DictG.description.label("Field"),
        WellHdr.well_name.label("Well"),
        Pressure.cid.label("Reservoir"),
        func.trunc(Pressure.test_date, "month").cast(Date).label("Date"),
        Pressure.source.label("Source_resp"),
        (
            func.coalesce(
                Pressure.owc_resp_arm,
                Pressure.owc_resp_in1p,
                Pressure.owc_resp_inwt,
            )
            * 10.2
        ).label("Pres"),
    ).where(
        Pressure.field == DictG.id,
        Pressure.uwi == WellHdr.uwi,
        or_(
            Pressure.owc_resp_arm.is_not(None),
            Pressure.owc_resp_in1p.is_not(None),
            Pressure.owc_resp_inwt.is_not(None),
        ),
        Pressure.source.in_(("Сиам", "OIS Gen", "Геолог УН")),
        (DictG.description + WellHdr.well_name + Pressure.cid).in_(
            bindparam("uids")
        ),
    )
