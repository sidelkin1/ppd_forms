from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex import ofm
from app.infrastructure.db.dao.complex.loader.ofm_loader import OfmLoader


@dataclass
class MonthlyReportLoader(
    OfmLoader[ofm.MonthlyReportDAO, local.MonthlyReportDAO]
):
    pass
