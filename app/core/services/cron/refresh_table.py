import logging
from datetime import date
from typing import Any

from arq import Retry
from colorama import Fore
from dateutil.relativedelta import relativedelta

from app.core.context import WorkerContext
from app.infrastructure.db.dao.complex.loaders import (
    monthly_report_loader,
    well_profile_loader,
)
from app.infrastructure.db.dao.complex.loaders.ofm_loader import (
    OfmLoader,
    OfmLoaderFactory,
)
from app.infrastructure.exceptions import OfmPoolNotConfiguredError

logger = logging.getLogger(__name__)


async def _refresh_table(
    table: str,
    loader_factory: OfmLoaderFactory[OfmLoader],
    date_from: date,
    date_to: date,
    ctx: dict[str, Any],
) -> None:
    if ctx["job_try"] == 1:
        logger.info(
            "Refreshing %s%s%s",
            Fore.YELLOW,
            table,
            Fore.RESET,
            extra={"date_from": date_from, "date_to": date_to},
        )
    app: WorkerContext = ctx["app"]
    try:
        with app.sessions.ofm_session() as ofm_session:
            async with app.sessions.local_session() as local_session:
                loader = loader_factory(local_session, ofm_session)
                await loader.refresh(date_from=date_from, date_to=date_to)
    except OfmPoolNotConfiguredError:
        # Неисправимая ошибка конфигурации — ретраить бессмысленно.
        raise
    except Exception as error:
        # Ошибки соединения с Oracle и прочие — исправимые, уходим в Retry.
        logger.error(
            "%s%s%s refreshing failed",
            Fore.YELLOW,
            table,
            Fore.RESET,
            exc_info=error,
        )
        defer = ctx["job_try"] * 2
        logger.info(
            "Retrying refreshing %s%s%s in %ss",
            Fore.YELLOW,
            table,
            Fore.RESET,
            defer,
        )
        raise Retry(defer=defer)
    logger.info("%s%s%s was refreshed", Fore.YELLOW, table, Fore.RESET)


async def cron_refresh_mer(ctx: dict[str, Any]) -> None:
    date_from = date_to = date.today().replace(day=1) - relativedelta(months=1)
    await _refresh_table("MER", monthly_report_loader, date_from, date_to, ctx)


async def cron_refresh_opp(ctx: dict[str, Any]) -> None:
    date_from = date.today() - relativedelta(months=2)
    date_to = date.today()
    await _refresh_table("OPP", well_profile_loader, date_from, date_to, ctx)
