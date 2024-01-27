from sqlalchemy.orm import Session

from app.core.models.dto import MonthlyReportDB, WellProfileDB
from app.infrastructure.db.dao.sql.ofm import MonthlyReportDAO, WellProfileDAO


class MonthlyReportMock(MonthlyReportDAO):
    def __init__(self, session: Session) -> None:
        pass

    async def get_by_params(self, **params) -> list[MonthlyReportDB]:
        return [
            MonthlyReportDB(
                field="F2",
                well_name="W100",
                cid_all="R1,R2",
                cid="R1",
                dat_rep="2000-01-01",
                oil=1,
                oil_v=2,
                water_v=3,
                water=0,
                days=1,
            )
        ]


class WellProfileMock(WellProfileDAO):
    def __init__(self, session: Session) -> None:
        pass

    async def get_by_params(self, **params) -> list[WellProfileDB]:
        return [
            WellProfileDB(
                field="F2",
                uwi="F2W100",
                well_name="W100",
                well_type="Type",
                rec_date="2000-01-01",
                cid_all="R1,R2",
                cid_layer="R1",
                layer="L1",
                top=1000,
                bottom=2000,
                abstop=-1000,
                absbotm=-2000,
                diff_absorp=100,
                tot_absorp=100,
                liq_rate=100,
                remarks=None,
            )
        ]
