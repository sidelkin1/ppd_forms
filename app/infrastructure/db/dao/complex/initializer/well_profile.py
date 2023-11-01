from dataclasses import dataclass

from app.infrastructure.db.dao import csv, local
from app.infrastructure.db.dao.complex.initializer.base import BaseInitializer


@dataclass
class WellProfileInitializer(
    BaseInitializer[csv.WellProfileDAO, local.WellProfileDAO]
):
    pass
