from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.initializer.base import BaseInitializer
from app.infrastructure.files.dao import csv


@dataclass
class ReservoirReplaceInitializer(
    BaseInitializer[csv.ReservoirReplaceDAO, local.ReservoirReplaceDAO]
):
    pass
