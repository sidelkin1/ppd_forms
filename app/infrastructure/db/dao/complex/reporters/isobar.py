import asyncio
import logging
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import date
from typing import TypeVar, cast

import pandas as pd

from app.infrastructure.db.dao.sql import reporters as db
from app.infrastructure.files.dao import reporters as files

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def _timed(
    name: str, coro: Awaitable[T], timings: dict[str, float]
) -> T:
    start = time.perf_counter()
    result = await coro
    timings[f"time_{name}"] = round(time.perf_counter() - start, 1)
    return result


@dataclass
class IsobarReporter:
    stock: db.OfmIsobarReporter
    tests: db.LocalIsobarReporter
    previous: files.IsobarReporter

    async def read_all(
        self, *, stock_date: date, on_date: date, previous_date: date
    ) -> dict[str, pd.DataFrame]:
        start = time.perf_counter()
        prev_values = await self.previous.read_previous()
        timings: dict[str, float] = {
            "time_previous_file": round(time.perf_counter() - start, 1)
        }
        rows: list[tuple[str, str, date, str]] = sorted(
            {
                (
                    str(row.field),
                    str(row.well_nb),
                    cast(date, row.prev_date),
                    str(row.reservoir),
                )
                for row in prev_values.dropna(
                    subset=["prev_date", "well_nb", "reservoir"]
                ).itertuples()
            }
        )
        async with asyncio.TaskGroup() as tg:
            stock = tg.create_task(
                _timed(
                    "stock",
                    self.stock.read_one(
                        stock_date=stock_date, on_date=on_date
                    ),
                    timings,
                )
            )
            succeeded = tg.create_task(
                _timed(
                    "succeeded",
                    self.tests.read_one(
                        key="succeeded",
                        date_from=previous_date,
                        date_to=on_date,
                    ),
                    timings,
                )
            )
            failed = tg.create_task(
                _timed(
                    "failed",
                    self.tests.read_one(
                        key="failed",
                        date_from=previous_date,
                        date_to=on_date,
                    ),
                    timings,
                )
            )
            prev_state = tg.create_task(
                _timed(
                    "prev_state",
                    self.tests.read_previous(rows),
                    timings,
                )
            )
        logger.info(
            "Изобары, чтение данных",
            extra={
                "time_total": round(time.perf_counter() - start, 1),
                **timings,
            },
        )
        prev_state_df = prev_state.result()
        stock_df = stock.result()
        succeeded_df = succeeded.result()
        missing = _missing_keys(rows, prev_state_df)
        if not missing.empty:
            missing = missing.merge(
                _previous_info(prev_values),
                on=["field", "well", "end_date", "reservoir"],
                how="left",
                validate="many_to_one",
            )
        return {
            "stock": stock_df,
            "succeeded": succeeded_df,
            "failed": failed.result(),
            "prev_state": prev_state_df,
            "prev_missing": missing,
            "prev_unmatched": _unmatched_previous(prev_values, stock_df),
            "test_unmatched": _unmatched_tests(succeeded_df, stock_df),
            "prev_values": prev_values,
        }


_LOST_COLUMNS = [
    "field",
    "well",
    "reservoir",
    "well_test",
    "resp",
    "end_date",
]


def _stock_keys(stock: pd.DataFrame) -> set[tuple[object, ...]]:
    return set(zip(stock["field"], stock["well_name"], stock["cid"]))


def _unmatched_previous(
    prev_values: pd.DataFrame, stock: pd.DataFrame
) -> pd.DataFrame:
    """Строки предыдущей сводной с Рпл, которым нет пары в фонде."""
    if prev_values.empty or stock.empty:
        return pd.DataFrame(columns=_LOST_COLUMNS)
    data = prev_values[prev_values["prev_resp"].notna()]
    keys = _stock_keys(stock)
    unmatched = data[
        [
            (field, well, reservoir) not in keys
            for field, well, reservoir in zip(
                data["field"], data["well"], data["reservoir"]
            )
        ]
    ]
    return (
        pd.DataFrame(
            {
                "field": unmatched["field"],
                "well": unmatched["well"],
                "reservoir": unmatched["reservoir"],
                "well_test": unmatched["prev_well_test"],
                "resp": unmatched["prev_resp"].round(2),
                "end_date": unmatched["prev_date"],
            }
        )
        .sort_values(_LOST_COLUMNS)
        .reset_index(drop=True)
    )


def _unmatched_tests(
    succeeded: pd.DataFrame, stock: pd.DataFrame
) -> pd.DataFrame:
    """Текущие замеры welltest с Рпл, которым нет пары в фонде.

    ``welltest.well`` хранится без ствола, а в фонде скважина может быть
    со стволом, поэтому сверяем с ``parent`` (скважина без ствола) — по
    нему же идёт склейка текущих замеров.
    """
    if succeeded.empty or stock.empty:
        return pd.DataFrame(columns=_LOST_COLUMNS)
    keys = set(zip(stock["field"], stock["parent"], stock["cid"]))
    unmatched = succeeded[
        [
            (field, well, reservoir) not in keys
            for field, well, reservoir in zip(
                succeeded["field"],
                succeeded["well"],
                succeeded["reservoir"],
            )
        ]
    ].rename(columns={"resp_owc": "resp"})
    unmatched["resp"] = unmatched["resp"].round(2)
    return (
        unmatched[_LOST_COLUMNS]
        .sort_values(_LOST_COLUMNS)
        .reset_index(drop=True)
    )


def _previous_info(prev_values: pd.DataFrame) -> pd.DataFrame:
    """Вид исследования и Рпл из строки предыдущей сводной."""
    info = pd.DataFrame(
        {
            "field": prev_values["field"],
            "well": prev_values["well_nb"],
            "end_date": prev_values["prev_date"],
            "reservoir": prev_values["reservoir"],
            "well_test": prev_values["prev_well_test"],
            "resp": prev_values["prev_resp"],
        }
    )
    return info.drop_duplicates(
        subset=["field", "well", "end_date", "reservoir"], keep="first"
    )


def _missing_keys(
    rows: list[tuple[str, str, date, str]], found: pd.DataFrame
) -> pd.DataFrame:
    """Ключи предыдущих замеров, для которых не нашлось записи в welltest."""
    columns = ["field", "well", "end_date", "reservoir"]
    if not rows:
        return pd.DataFrame(columns=columns)
    requested = set(rows)
    matched = set(
        zip(
            found["field"],
            found["well"],
            found["end_date"],
            found["reservoir"],
        )
    )
    return pd.DataFrame(sorted(requested - matched), columns=columns)
