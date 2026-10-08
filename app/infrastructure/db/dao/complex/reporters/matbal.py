from dataclasses import dataclass

import pandas as pd

from app.core.models.dto import UneftReservoirDB
from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.db.mappers import well_no_cache_mapper


def _normalize_wells(wells: list[str]) -> list[str]:
    return [
        well_no_cache_mapper[well.strip()] for well in wells if well.strip()
    ]


@dataclass
class MatbalReporter:
    field: db.FieldMatbalReporter
    field_alt: db.AltFieldMatbalReporter
    wells: db.WellMatbalReporter
    wells_alt: db.AltWellMatbalReporter

    async def read_all(
        self,
        *,
        field_id: int,
        reservoirs: list[UneftReservoirDB],
        wells: list[str],
        alternative: bool,
    ) -> dict[str, pd.DataFrame]:
        wells = _normalize_wells(wells)
        names = [item.name for item in reservoirs]
        ids = [str(item.id) for item in reservoirs]
        match wells, alternative:
            case [], False:
                return await self.field.read_all(
                    field_id=field_id, reservoirs=names, reservoir_ids=ids
                )
            case [], True:
                return await self.field_alt.read_all(
                    field_id=field_id, reservoirs=names, reservoir_ids=ids
                )
            case _, False:
                return await self.wells.read_all(
                    field_id=field_id,
                    reservoirs=names,
                    reservoir_ids=ids,
                    wells=wells,
                )
            case _, True:
                return await self.wells_alt.read_all(
                    field_id=field_id,
                    reservoirs=names,
                    reservoir_ids=ids,
                    wells=wells,
                )
        raise ValueError("Unsupported input arguments!")
