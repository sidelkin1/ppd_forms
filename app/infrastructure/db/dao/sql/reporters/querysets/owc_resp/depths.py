from sqlalchemy import func, select
from sqlalchemy.sql.expression import Select

from app.infrastructure.db.models.ofm.reflected import WellDirSrvyPts, WellHdr

from .branches import select_well_branch


def select_depths() -> Select:
    branch_uwi = func.coalesce(WellHdr.parent_uwi, WellHdr.uwi)
    return (
        select(
            WellDirSrvyPts.md,
            WellDirSrvyPts.tvd,
            (WellDirSrvyPts.md - WellDirSrvyPts.tvd).label("offset"),
        )
        .where(
            WellHdr.uwi.in_(select_well_branch()),
            WellDirSrvyPts.uwi == branch_uwi,
            WellDirSrvyPts.dir_srvy_id == "SRVY_1",
        )
        .order_by(WellDirSrvyPts.md)
    )
