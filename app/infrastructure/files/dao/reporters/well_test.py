import logging
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

import openpyxl
import pandas as pd
from fastapi.concurrency import run_in_threadpool
from openpyxl.drawing.image import Image
from openpyxl.reader.excel import SUPPORTED_FORMATS
from python_calamine import CalamineSheet, CalamineWorkbook

from app.core.models.dto import WellTestResult
from app.infrastructure.db.mappers import (
    BaseMapper,
    field_mapper,
    multi_split_reservoir_mapper,
    reservoir_mapper,
    well_mapper,
)
from app.infrastructure.utils.convert_to_xlsx import convert_to_xlsx

logger = logging.getLogger(__name__)


def _date_format(input_: Any) -> date:
    result = pd.to_datetime(
        input_, format="%d.%m.%Y %H:%M:%S", errors="coerce"
    ).date()
    if result is pd.NaT:
        result = pd.to_datetime(input_).date()
    return result


class WellTestReporter:
    interpretation_sheet = "Интерпретация"
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
        "permeability": r"Проницаемость(?:[\s\(]*по\s+жидкости[\s\)]*)?\s*$",
        "skin_factor": (
            r"^(?:(?:полный|сово?в?о?к?куп?а?ный)\s+)?"
            r"скин\s*-?\s*фактор(?:\s*,\s*St?)?\s*$"
        ),
        "resp_owc": r"пластовое давление на ВНК\s*$",
        "prod_index": (
            r"Коэффициент (?:продуктивности|при[её]мистости)\s*"
            r"(?:[\s\(]*(?:по\s+КПД|оценочно)[\s\)]*)?\s*$"
        ),
        "frac_length": (
            r"^(?:суммарная\s+)?"
            r"полудлина\s+трещины?,?\s*(?:[XХ]f)?\s*"
            r"(?:[\s\(]*оценочно[\s\)]*)?\s*$"
        ),
    }
    reservoir_numeric_parameters = {
        "permeability": r"Проницаемость.*{}",
        "skin_factor": (
            r"^(?:(?:полный|сово?в?о?к?куп?а?ный)\s+)?"
            r"скин\s*-?\s*фактор.*{}"
        ),
        "resp_owc": r"пластовое давление на ВНК.*{}",
        "prod_index": r"Коэффициент (?:продуктивности|при[её]мистости).*{}",
        "frac_length": r"полудлина\s+трещины?,?\s*(?:[XХ]f)?.*{}",
    }
    reservoir_cell = 8

    front_sheet = "Титульный"
    purpose_title = "Цель"
    interpreter_title = "Интерпретатор"

    convert_timeout_s = 10.0

    def __init__(self, path: Path, delimiter: str) -> None:
        self.path = path
        self.delimiter = delimiter

    def _read_report(self) -> pd.DataFrame:
        # Все столбцы с нужной информацией находятся в начале листа,
        # их кол-во обычно 4, но иногда может быть 5,
        # тогда последние 2 столбца обрабатываются отдельно,
        # все остальные столбцы отбрасываем
        df = pd.read_excel(  # type: ignore[call-overload]
            self.path,
            sheet_name=self.interpretation_sheet,
            engine="calamine",
        ).iloc[:, : len(self.columns) + 1]
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
                str(df.loc[self.reservoir_cell, "value"]).replace("\n", "")
            )
        ]

    def _get_isobars(self) -> Image | None:
        try:
            wb = openpyxl.load_workbook(self.path)
            ws = wb["Доп.данные"]
            image = ws._images[0]  # type: ignore[attr-defined]
        except Exception as error:
            image = None
            logger.error(
                "Не удалось извлечь изображение с картой изобар",
                exc_info=error,
                extra={"path": self.path},
            )
        return image

    def _search_purpose(self, ws: CalamineSheet) -> str:
        rows = ws.iter_rows()
        # Сначала ищем строку, содержащую ячейку "Цель"
        for row in rows:
            iter_row = map(str, row)
            value = next(filter(bool, iter_row), "")
            if self.purpose_title in value:
                break
        else:
            return ""
        # "Типовая" цель исследования
        purpose = next(filter(bool, iter_row), "")
        # Пробуем найти "уточненную" цель исследования
        for row in rows:
            iter_row = map(str, row)
            value = next(filter(bool, iter_row), "")
            if self.interpreter_title in value:
                return purpose
            elif value:
                purpose = value
        return purpose

    def _get_purpose(self) -> str:
        with CalamineWorkbook.from_path(self.path) as wb:
            ws = wb.get_sheet_by_name(self.front_sheet)
            purpose = self._search_purpose(ws)
            purpose = purpose.strip().replace("\n", " ")
        return purpose

    def _get_results(self) -> list[WellTestResult]:
        df = self._read_report()
        common_parameters = self._get_common_parameters(df)
        numeric_parameters = self._get_numeric_parameters(df)
        reservoirs = self._get_raw_reservoirs(df)
        isobars = self._get_isobars()
        purpose = self._get_purpose()
        return [
            cast(
                WellTestResult,
                common_parameters
                | {"reservoir": reservoir_mapper[reservoir]}
                | numeric_parameters
                | self._get_reservoir_parameters(df, reservoir)
                | {"isobars": isobars}
                | {"purpose": purpose},
            )
            for reservoir in reservoirs
        ]

    async def get_results(self) -> list[WellTestResult]:
        if self.path.suffix not in SUPPORTED_FORMATS:
            try:
                self.path = await convert_to_xlsx(
                    self.path, self.convert_timeout_s
                )
            except Exception as error:
                logger.error(
                    "Не удалось преобразовать файл в новый формат `xlsx`",
                    exc_info=error,
                    extra={"path": self.path},
                )
        return await run_in_threadpool(self._get_results)
