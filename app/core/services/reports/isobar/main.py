"""Точка входа отчёта «Сводная таблица для карт изобар»."""

import logging
import time
from datetime import date
from pathlib import Path
from shutil import make_archive
from typing import Any

from app.core.utils.process_pool import ProcessPoolManager
from app.infrastructure.db.dao.complex.reporters import IsobarReporter

from .columns import OUTPUT_PREFIX
from .workbook import process_workbook

logger = logging.getLogger(__name__)


def _log_diagnostics(result: dict[str, Any]) -> None:
    """Пишет предупреждения, которые вернул воркер."""
    for message in result["diagnostics"]:
        logger.warning(message)


async def isobar_report(
    path: Path,
    template: Path,
    previous_date: date,
    on_date: date,
    stock_date: date,
    dao: IsobarReporter,
    pool: ProcessPoolManager,
) -> None:
    """Собирает сводную: данные, диагностика, книга и архив.

    ``path`` — папка результата, ``template`` — загруженный шаблон,
    ``previous_date``/``on_date`` — границы квартала, ``stock_date`` —
    дата фонда (за месяц до ``on_date``).
    """
    start = time.perf_counter()
    dfs = await dao.read_all(
        stock_date=stock_date,
        on_date=on_date,
        previous_date=previous_date,
    )
    read = time.perf_counter() - start
    # отчёт — копия загруженной книги, поэтому расширение берём у шаблона
    suffix = template.suffix or ".xlsm"
    target = path / f"{OUTPUT_PREFIX}_{on_date:%d.%m.%Y}{suffix}"
    start = time.perf_counter()
    result = await pool.run(process_workbook, dfs, on_date, template, target)
    worker = time.perf_counter() - start
    start = time.perf_counter()
    make_archive(str(path), "zip", root_dir=path)
    archive = time.perf_counter() - start
    _log_diagnostics(result)
    logger.info(
        "Изобары, тайминги",
        extra={
            "time_read": round(read, 1),
            "time_worker": round(worker, 1),
            "time_zip": round(archive, 1),
            **result["timings"],
        },
    )
    logger.info("Изобары, статистика", extra=result["stats"])
