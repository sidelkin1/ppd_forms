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
                "poro_alt": fnv.select_poro_alt(),
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

    async def poro(self, alternative: bool, uwi: str) -> pd.DataFrame:
        if alternative:
            return await self.read_one(key="poro_alt", uwi=uwi)
        return await self.read_one(key="poro", uwi=uwi)

    async def events(self, alternative: bool, uwi: str) -> pd.DataFrame:
        if alternative:
            events = await self.read_one(key="events_alt", uwi=uwi)
            events["type_action"] = events["type_action"].map(
                lambda x: (
                    "SQUEEZE"
                    if "заливка" in x.lower()
                    else "PERFORATION"
                    if x != "GDI"
                    else "GDI"
                )
            )
            return events
        return await self.read_one(key="events", uwi=uwi)

    async def totwat(self, uwi: str, date_from: str, date_to: str) -> float:
        totwat = await self.read_one(
            key="totwat", uwi=uwi, date_from=date_from, date_to=date_to
        )
        return totwat.squeeze() or 0
