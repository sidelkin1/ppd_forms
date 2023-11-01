from dataclasses import dataclass

from app.infrastructure.db.dao import csv, local
from app.infrastructure.db.dao.complex.initializer.base import BaseInitializer


@dataclass
class LayerReplaceInitializer(
    BaseInitializer[csv.LayerReplaceDAO, local.LayerReplaceDAO]
):
    pass
