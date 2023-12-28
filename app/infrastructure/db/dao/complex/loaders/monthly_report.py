from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.ofm_loader import OfmLoader
from app.infrastructure.db.dao.sql import ofm


@dataclass
class MonthlyReportLoader(
    OfmLoader[ofm.MonthlyReportDAO, local.MonthlyReportDAO]
):
    pass
