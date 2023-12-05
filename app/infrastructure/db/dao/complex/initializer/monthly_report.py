from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.initializer.base import BaseInitializer
from app.infrastructure.file.dao import csv


@dataclass
class MonthlyReportInitializer(
    BaseInitializer[csv.MonthlyReportDAO, local.MonthlyReportDAO]
):
    pass
