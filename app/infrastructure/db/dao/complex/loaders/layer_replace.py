from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.csv_loader import CsvLoader
from app.infrastructure.files.dao import csv


@dataclass
class LayerReplaceLoader(
    CsvLoader[csv.LayerReplaceDAO, local.LayerReplaceDAO]
):
    pass
