from datetime import date
from pathlib import Path

import pandas as pd
from fastapi.concurrency import run_in_threadpool

from app.infrastructure.db.mappers import (
    field_mapper,
    multi_well_mapper,
    reservoir_mapper,
    well_mapper,
)


class MatrixReporter:
    converters = {
        "М-е": lambda s: field_mapper[str(s)],
        "№ скв.": lambda s: well_mapper[str(s)],
        "Объект": lambda s: reservoir_mapper[str(s)],
        "Округа": lambda s: multi_well_mapper[str(s)],
        "Дата": lambda s: pd.to_datetime(s, format="%d.%m.%Y").date(),
    }
    usecols = [
        "М-е",
        "№ скв.",
        "Объект",
        "Дата",
        "ГТМ",
        "Округа",
        "Проблемность",
        "Описание ГТМ",
    ]
    columns = [
        "field",
        "well",
        "reservoir",
        "gtm_date",
        "gtm_group",
        "neighbs",
        "gtm_problem",
        "gtm_description",
    ]
    dropna_columns = [
        "field",
        "well",
        "reservoir",
        "gtm_date",
        "gtm_group",
        "neighbs",
    ]
    fillna_columns = [
        "gtm_problem",
        "gtm_description",
    ]

    def __init__(self, path: Path, wells: str | None) -> None:
        self.wells = path / wells if wells else None

    def _load_wells(
        self, date_from: date, date_to: date
    ) -> pd.DataFrame | None:
        if self.wells is None:
            return None
        df = pd.read_excel(  # type: ignore
            self.wells,
            engine="openpyxl",
            converters=self.converters,
            usecols=self.usecols,
        )
        df.columns = self.columns  # type: ignore
        df = (
            df.dropna(subset=self.dropna_columns)
            .assign(reservoir_neighbs=None)
            .loc[df["gtm_date"].between(date_from, date_to)]
        )
        df[self.fillna_columns] = df[self.fillna_columns].fillna("")
        return df

    async def get_wells(
        self, *, date_from: date, date_to: date
    ) -> pd.DataFrame | None:
        df = await run_in_threadpool(self._load_wells, date_from, date_to)
        return df
