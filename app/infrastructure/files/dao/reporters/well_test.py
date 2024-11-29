import re
from datetime import date
from pathlib import Path
from typing import Any, cast

import pandas as pd
from fastapi.concurrency import run_in_threadpool

from app.core.models.dto import WellTestResult
from app.infrastructure.db.mappers import (
    BaseMapper,
    field_mapper,
    multi_split_reservoir_mapper,
    reservoir_mapper,
    well_mapper,
)


def _date_format(input_: Any) -> date:
    result = pd.to_datetime(
        input_, format="%d.%m.%Y %H:%M:%S", errors="coerce"
    ).date()
    if result is pd.NaT:
        result = pd.to_datetime(input_).date()
    return result


class WellTestReporter:
    sheet_name = "Интерпретация"
    columns = ["key", "units", "value", "source"]
    common_parameters = {
        "well_test": "Вид исследования",
        "field": "Месторождение",
        "well": "Номер скважины",
        "well_type": "Назначение скважины",
        "end_date": "Дата/время окончания исследования",
        "reliability": r"Достоверность\s*/",
    }
    common_converters = {
        "field": lambda s: field_mapper[s],
        "well": lambda s: well_mapper[s],
        "end_date": _date_format,
    }
    numeric_parameters = {
        "permeability": r"Проницаемость\s*$",
        "skin_factor": r"^(?:Совокупный\s+)?скин\s*-?\s*фактор(?:,\s*S)?\s*$",
        "resp_owc": r"пластовое давление на ВНК\s*$",
        "prod_index": r"Коэффициент (?:продуктивности|при[её]мистости)\s*$",
        "frac_length": r"Полудлина трещины, Xf\s*$",
    }
    reservoir_numeric_parameters = {
        "permeability": r"Проницаемость.*{}",
        "skin_factor": r"^(?:Совокупный\s+)?скин\s*-?\s*фактор.*{}",
        "resp_owc": r"пластовое давление на ВНК.*{}",
        "prod_index": r"Коэффициент (?:продуктивности|при[её]мистости).*{}",
        "frac_length": r"Полудлина трещины, Xf.*{}",
    }
    reservoir_cell = 8

    def __init__(self, path: Path, delimiter: str) -> None:
        self.path = path
        self.delimiter = delimiter

    def _read_report(self) -> pd.DataFrame:
        # Все столбцы с нужной информацией находятся в начале листа,
        # их кол-во обычно 4, но иногда может быть 5,
        # тогда последние 2 столбца обрабатываются отдельно,
        # все остальные столбцы отбрасываем
        df = pd.read_excel(self.path, sheet_name=self.sheet_name).iloc[
            :, : len(self.columns) + 1
        ]
        if len(df.columns) > len(self.columns):
            # Если кол-во столбцов в отчете на 1 больше, чем нужно
            df.iloc[:, -2] = df.iloc[:, -2].fillna(df.iloc[:, -1])
            df = df.iloc[:, :-1]
        df.columns = self.columns  # type: ignore[assignment]
        return df

    def _find_parameter(self, df: pd.DataFrame, pattern: str) -> str:
        match = df.loc[
            df["key"].str.contains(pattern, na=False, flags=re.IGNORECASE),
            "value",
        ]
        return "" if match.empty else str(match.squeeze())

    def _parse_numeric(self, df: pd.DataFrame, pattern: str) -> float:
        return pd.to_numeric(
            self._find_parameter(df, pattern).replace(",", "."),
            errors="coerce",
        )

    def _get_common_parameters(self, df: pd.DataFrame) -> dict[str, Any]:
        return {
            key: self.common_converters[key](value)
            if key in self.common_converters
            else value
            for key, pattern in self.common_parameters.items()
            if (value := self._find_parameter(df, pattern))
        }

    def _get_numeric_parameters(self, df: pd.DataFrame) -> dict[str, Any]:
        return {
            key: self._parse_numeric(df, pattern)
            for key, pattern in self.numeric_parameters.items()
        }

    def _get_reservoir_parameters(
        self, df: pd.DataFrame, resevoir: str
    ) -> dict[str, Any]:
        return {
            key: value
            for key, pattern in self.reservoir_numeric_parameters.items()
            if pd.notna(
                value := self._parse_numeric(
                    df, pattern.format(re.escape(resevoir))
                )
            )
        }

    def _get_raw_reservoirs(self, df: pd.DataFrame) -> list[str]:
        return [
            reservoir[BaseMapper.WORD]
            for reservoir in multi_split_reservoir_mapper.split_words(
                str(df.loc[self.reservoir_cell, "value"])
            )
        ]

    def _get_results(self) -> list[WellTestResult]:
        df = self._read_report()
        common_parameters = self._get_common_parameters(df)
        numeric_parameters = self._get_numeric_parameters(df)
        reservoirs = self._get_raw_reservoirs(df)
        return [
            cast(
                WellTestResult,
                common_parameters
                | {"reservoir": reservoir_mapper[reservoir]}
                | numeric_parameters
                | self._get_reservoir_parameters(df, reservoir),
            )
            for reservoir in reservoirs
        ]

    async def get_results(self) -> list[WellTestResult]:
        return await run_in_threadpool(self._get_results)
