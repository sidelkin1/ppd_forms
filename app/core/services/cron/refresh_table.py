import logging
from datetime import date
from typing import Any, cast

from arq import Retry
from colorama import Fore
from dateutil.relativedelta import relativedelta

from app.infrastructure.db.dao.complex.loaders.ofm_loader import OfmLoader
from app.infrastructure.holder import HolderDAO

logger = logging.getLogger(__name__)


async def _refresh_table(
    table: str, dao: str, date_from: date, date_to: date, ctx: dict[str, Any]
) -> None:
    if ctx["job_try"] == 1:
        logger.info(
            "Refreshing %s%s%s",
            Fore.YELLOW,
            table,
            Fore.RESET,
            extra={"date_from": date_from, "date_to": date_to},
        )
    try:
        async with ctx["ofm_local_dao"]() as holder:
            holder = cast(HolderDAO, holder)
            dao_: OfmLoader = getattr(holder, dao)
            await dao_.refresh(date_from=date_from, date_to=date_to)
    except Exception as error:
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
    await _refresh_table(
        "MER", "monthly_report_loader", date_from, date_to, ctx
    )


async def cron_refresh_opp(ctx: dict[str, Any]) -> None:
    date_from = date.today() - relativedelta(months=2)
    date_to = date.today()
    await _refresh_table("OPP", "well_profile_loader", date_from, date_to, ctx)
