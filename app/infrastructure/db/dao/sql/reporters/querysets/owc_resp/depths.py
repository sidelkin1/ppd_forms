from sqlalchemy import bindparam, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import WellDirSrvyPts, WellHdr


def select_depths() -> Select:
    return (
        select(
            WellDirSrvyPts.md,
            WellDirSrvyPts.tvd,
            (WellDirSrvyPts.md - WellDirSrvyPts.tvd).label("offset"),
        )
        .where(
            WellHdr.uwi == WellDirSrvyPts.uwi,
            WellHdr.well_name == bindparam("well"),
            WellHdr.field == bindparam("field_id"),
            WellDirSrvyPts.dir_srvy_id == "SRVY_1",
        )
        .order_by(WellDirSrvyPts.md)
    )
