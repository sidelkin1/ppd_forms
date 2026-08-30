import logging
from collections.abc import Callable
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.enums import ExcelTableName, OfmTableName
from app.infrastructure.db.dao import local

logger = logging.getLogger(__name__)

_dao_mapper: dict[
    ExcelTableName | OfmTableName,
    Callable[[AsyncSession], local.MainTableDAO[Any, Any]],
] = {
    OfmTableName.report: local.MonthlyReportDAO,
    OfmTableName.profile: local.WellProfileDAO,
    ExcelTableName.ns_ppd: local.NewStrategyInjDAO,
    ExcelTableName.ns_oil: local.NewStrategyOilDAO,
    ExcelTableName.inj_db: local.InjWellDatabaseDAO,
    ExcelTableName.neighbs: local.NeighborhoodDAO,
    ExcelTableName.gdis: local.WellTestDAO,
}


async def date_range(
    table: ExcelTableName | OfmTableName, session: AsyncSession
) -> tuple[date, date]:
    logger.debug("Getting dates", extra={"table": table})
    dao = _dao_mapper[table](session)
    return await dao.date_range()
