from datetime import date

from app.core.models.enums import ExcelTableName, OfmTableName
from app.infrastructure.db.dao.holder import HolderDAO
from app.infrastructure.db.dao.local import MainTableDAO

_dao_mapper = {
    OfmTableName.report: "local_monthly_report",
    OfmTableName.profile: "local_well_profile",
    ExcelTableName.ns_ppd: "local_new_strategy_inj",
    ExcelTableName.ns_oil: "local_new_strategy_oil",
    ExcelTableName.inj_db: "local_inj_well_database",
    ExcelTableName.neighbs: "local_neighborhood",
}


async def date_range(
    table: ExcelTableName | OfmTableName, holder: HolderDAO
) -> tuple[date, date]:
    dao: MainTableDAO = getattr(holder, _dao_mapper[table])
    return await dao.date_range()
