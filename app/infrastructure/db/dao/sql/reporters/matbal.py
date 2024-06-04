import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO
from app.infrastructure.db.dao.sql.reporters.querysets import (
    select_field_sum_alternative_rates,
    select_field_sum_rates,
    select_well_sum_alternative_rates,
    select_well_sum_rates,
)


class MatbalReporter(OfmBaseDAO):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        super().__init__(
            {
                "field": select_field_sum_rates(),
                "wells": select_well_sum_rates(),
                "field_alt": select_field_sum_alternative_rates(),
                "wells_alt": select_well_sum_alternative_rates(),
            },
            pool,
        )

    async def get_field_rates(
        self, field_id: int, reservoirs: list[str], alternative: bool
    ) -> pd.DataFrame:
        if alternative:
            return await self.read_one(
                key="field_alt", field_id=field_id, reservoirs=reservoirs
            )
        return await self.read_one(
            key="field", field_id=field_id, reservoirs=reservoirs
        )

    async def get_well_rates(
        self,
        field_id: int,
        reservoirs: list[str],
        wells: list[str],
        alternative: bool,
    ) -> pd.DataFrame:
        if alternative:
            return await self.read_one(
                key="wells_alt",
                field_id=field_id,
                reservoirs=reservoirs,
                wells=wells,
            )
        return await self.read_one(
            key="wells", field_id=field_id, reservoirs=reservoirs, wells=wells
        )
