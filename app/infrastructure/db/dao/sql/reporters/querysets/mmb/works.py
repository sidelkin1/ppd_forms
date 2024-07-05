from sqlalchemy import Date, Select, bindparam, func, select

from app.infrastructure.db.models.ofm.reflected import DictG, Notes, WellHdr


def select_tank_works() -> Select:
    return select(
        DictG.description.label("Field"),
        WellHdr.well_name.label("Well"),
        Notes.cid.label("Reservoir"),
        func.trunc(Notes.dat_beg, "month").cast(Date).label("Date"),
        Notes.notes.label("Wellwork"),
    ).where(
        Notes.field == DictG.id,
        Notes.uwi == WellHdr.uwi,
        (DictG.description + WellHdr.well_name + Notes.cid).in_(
            bindparam("uids")
        ),
    )
