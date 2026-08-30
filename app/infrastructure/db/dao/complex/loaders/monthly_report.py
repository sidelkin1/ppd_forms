from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.ofm_loader import (
    OfmLoader,
    OfmLoaderFactory,
    ofm_loader_factory,
)
from app.infrastructure.db.dao.sql import ofm


@dataclass
class MonthlyReportLoader(
    OfmLoader[ofm.MonthlyReportDAO, local.MonthlyReportDAO]
):
    pass


monthly_report_loader: OfmLoaderFactory[MonthlyReportLoader] = (
    ofm_loader_factory(
        MonthlyReportLoader, ofm.MonthlyReportDAO, local.MonthlyReportDAO
    )
)
