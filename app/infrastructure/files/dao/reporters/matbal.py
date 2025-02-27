from pathlib import Path

import aiofiles
import pandas as pd
from fastapi.concurrency import run_in_threadpool

from app.infrastructure.db.mappers import multi_well_mapper


class MatbalReporter:
    converters = {
        "date": lambda s: pd.to_datetime(s, format="%d.%m.%Y").date()
    }

    def __init__(
        self, path: Path, wells: str | None, measurements: str | None
    ) -> None:
        self.wells = path / wells if wells else None
        self.measurements = path / measurements if measurements else None

    async def get_wells(self) -> list[str] | None:
        if self.wells is None:
            return None
        async with aiofiles.open(self.wells, encoding="utf8") as file:
            wells = multi_well_mapper[await file.read()].split(
                multi_well_mapper.delimiter
            )
        return wells

    async def get_measurements(self) -> pd.DataFrame | None:
        if self.measurements is None:
            return None
        df = await run_in_threadpool(
            pd.read_table,
            self.measurements,
            sep=r"\s+",
            names=["date", "Pres"],
            converters=self.converters,
        )
        return df
