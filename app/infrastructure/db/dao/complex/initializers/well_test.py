from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.initializers.base import BaseInitializer
from app.infrastructure.files.dao import csv


@dataclass
class WellTestInitializer(BaseInitializer[csv.WellTestDAO, local.WellTestDAO]):
    pass
