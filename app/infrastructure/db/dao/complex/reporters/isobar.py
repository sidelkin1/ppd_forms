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

_PREV_KEY_COLUMNS = ("prev_date", "well_nb", "reservoir")


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
        """Читает фонд, замеры, предыдущую сводную, M/N и перфорации."""
        start = time.perf_counter()
        timings: dict[str, float] = {}
        async with asyncio.TaskGroup() as tg:
            previous = tg.create_task(
                _timed(
                    "previous_file",
                    self.previous.read_previous(),
                    timings,
                )
            )
            stock = tg.create_task(
                _timed(
                    "stock",
                    self.stock.read_one(
                        key="stock",
                        stock_date=stock_date,
                        on_date=on_date,
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
        prev_values = previous.result()
        stock_df = stock.result()
        succeeded_df = succeeded.result()
        failed_df = failed.result()

        prev_keys = _previous_keys(prev_values)
        keys = _test_keys(succeeded_df, failed_df)
        async with asyncio.TaskGroup() as tg:
            prev_state = tg.create_task(
                _timed(
                    "prev_state",
                    self.tests.read_previous(prev_keys),
                    timings,
                )
            )
            perfs = tg.create_task(
                _timed(
                    "perfs",
                    self.stock.read_perfs(keys, previous_date),
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
        return {
            "stock": stock_df,
            "succeeded": succeeded_df,
            "failed": failed_df,
            "prev_state": prev_state.result(),
            "prev_values": prev_values,
            "perfs": perfs.result(),
        }


def _previous_keys(
    prev_values: pd.DataFrame,
) -> list[tuple[str, str, date, str]]:
    """Замеры предыдущей сводной, для которых читаются тип и состояние.

    Ключ — месторождение, скважина без ствола, дата замера, объект.
    """
    data = prev_values.dropna(subset=list(_PREV_KEY_COLUMNS))
    return sorted(
        {
            (
                str(field),
                str(well),
                cast(date, prev_date),
                str(reservoir),
            )
            for field, well, prev_date, reservoir in zip(
                data["field"],
                data["well_nb"],
                data["prev_date"],
                data["reservoir"],
            )
        }
    )


def _test_keys(*frames: pd.DataFrame) -> list[tuple[str, str, str]]:
    """Замеры квартала, для которых читаются перфорации.

    Ключ — месторождение, скважина без ствола, объект.
    """
    keys: set[tuple[str, str, str]] = set()
    for frame in frames:
        if frame.empty:
            continue
        keys.update(
            (str(field), str(well), str(reservoir))
            for field, well, reservoir in zip(
                frame["field"], frame["well"], frame["reservoir"]
            )
        )
    return sorted(keys)
