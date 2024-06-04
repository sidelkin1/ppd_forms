from dataclasses import dataclass

import pandas as pd

from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files


@dataclass
class MatbalReporter:
    rates: db.MatbalReporter
    files: files.MatbalReporter

    async def get_rates(
        self, field_id: int, reservoirs: list[str], alternative: bool
    ) -> pd.DataFrame:
        wells = await self.files.get_wells()
        if wells is None:
            return await self.rates.get_field_rates(
                field_id, reservoirs, alternative
            )
        return await self.rates.get_well_rates(
            field_id, reservoirs, wells, alternative
        )

    async def get_measurements(self) -> pd.DataFrame | None:
        return await self.files.get_measurements()
