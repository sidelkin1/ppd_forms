from dataclasses import dataclass

from app.infrastructure.db.dao import local
from app.infrastructure.db.dao.complex.loaders.ofm_loader import (
    OfmLoader,
    OfmLoaderFactory,
    ofm_loader_factory,
)
from app.infrastructure.db.dao.sql import ofm


@dataclass
class WellProfileLoader(OfmLoader[ofm.WellProfileDAO, local.WellProfileDAO]):
    pass


well_profile_loader: OfmLoaderFactory[WellProfileLoader] = ofm_loader_factory(
    WellProfileLoader, ofm.WellProfileDAO, local.WellProfileDAO
)
