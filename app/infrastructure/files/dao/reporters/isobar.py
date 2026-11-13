import logging
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi.concurrency import run_in_threadpool

from app.infrastructure.db.mappers import (
    field_mapper,
    reservoir_mapper,
    well_mapper,
    well_no_branch_mapper,
)

logger = logging.getLogger(__name__)


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _to_date(value: Any) -> date | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _to_optional_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def _to_number(value: Any) -> float | None:
    number = pd.to_numeric(str(value).replace(",", "."), errors="coerce")
    return None if pd.isna(number) else float(number)


class IsobarReporter:
    """Предыдущие значения Pпл из загруженной сводной «текущие отборы».

    Колонка D листа — дисплей-имена объектов («Башкирский»,
    «турнейский(рудинский)»); ``reservoir_mapper`` переводит их в локальные
    имена («Бш», «Тур», «Вр+Бш»). Это тот же домен, что ``cid`` (sdes) в OFM
    и ``welltest.reservoir`` в локальной БД.
    """

    sheet = "текущие отборы"
    converters = {
        "месторождение": lambda value: field_mapper[_to_text(value)],
        "объект работы": lambda value: reservoir_mapper[_to_text(value)],
        "№ скв": lambda value: well_mapper[_to_text(value)],
        "Рпл": _to_number,
        "дата": _to_date,
        "вид исследования": _to_optional_text,
    }
    usecols = [
        "месторождение",
        "объект работы",
        "№ скв",
        "Рпл",
        "дата",
        "вид исследования",
    ]
    columns = [
        "field",
        "reservoir",
        "well",
        "prev_resp",
        "prev_date",
        "prev_well_test",
    ]
    key_columns = ["field", "reservoir", "well"]

    def __init__(self, path: Path) -> None:
        self.path = path

    def _read_previous(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(  # type: ignore[call-overload]
                self.path,
                sheet_name=self.sheet,
                converters=self.converters,
                usecols=self.usecols,
                engine="calamine",
            )
        except Exception as error:
            raise ValueError(
                f"Не удалось прочитать файл «{self.path.name}»: {error}"
            ) from error
        df.columns = self.columns  # type: ignore[assignment]

        df = df[(df[self.key_columns] != "").all(axis=1)].copy()
        df["well_nb"] = df["well"].map(well_no_branch_mapper.__getitem__)

        unique = df.drop_duplicates(subset=self.key_columns)
        if len(unique) != len(df):
            logger.warning(
                "Дубли в предыдущей сводной: %d строк",
                len(df) - len(unique),
            )
        without_date = unique[
            unique["prev_resp"].notna() & unique["prev_date"].isna()
        ]
        if not without_date.empty:
            logger.warning(
                "В предыдущей сводной %d строк с Рпл без распознанной даты "
                "(например: %s)",
                len(without_date),
                ", ".join(
                    f"{field} {well}"
                    for field, well in zip(
                        without_date["field"], without_date["well"]
                    )
                )[:200],
            )
        return unique[[*self.columns, "well_nb"]].reset_index(drop=True)

    async def read_previous(self) -> pd.DataFrame:
        return await run_in_threadpool(self._read_previous)
