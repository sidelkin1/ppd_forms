import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import fnv


class FnvReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "cumwat": fnv.select_cumwat(),
                "layers": fnv.select_layers(),
                "poro": fnv.select_poro(),
                "events": fnv.select_events(),
                "events_alt": fnv.select_events_alt(),
                "totwat": fnv.select_totwat(),
            },
            pool,
        )

    async def cumwat(self, field_id: int) -> pd.DataFrame:
        return await self.read_one(key="cumwat", field_id=field_id)

    async def layers(self, field_id: int) -> pd.DataFrame:
        return await self.read_one(key="layers", field_id=field_id)

    async def poro(self, uwi: str) -> pd.DataFrame:
        return await self.read_one(key="poro", uwi=uwi)

    async def events(self, alternative: bool, uwi: str) -> pd.DataFrame:
        return await (
            self.read_one(key="events_alt", uwi=uwi)
            if alternative
            else self.read_one(key="events", uwi=uwi)
        )

    async def totwat(
        self, uwi: str, date_from: str, date_to: str
    ) -> pd.DataFrame:
        return await self.read_one(
            key="totwat", uwi=uwi, date_from=date_from, date_to=date_to
        )
