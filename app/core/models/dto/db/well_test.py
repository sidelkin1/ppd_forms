from datetime import date

from pydantic import BaseModel, ConfigDict

from app.core.models.dto.db.validators import EmptyStrOrNanToNone, NanToNone


class WellTestDB(BaseModel):
    id: int | None = None
    well: str
    field: str
    reservoir: str
    well_type: EmptyStrOrNanToNone[str]
    well_test: str
    start_date: date
    end_date: date
    oil_perm: NanToNone[float]
    wat_perm: NanToNone[float]
    liq_perm: NanToNone[float]
    skin_factor: NanToNone[float]
    resp_owc: NanToNone[float]
    prod_index: NanToNone[float]
    reliability: EmptyStrOrNanToNone[str]

    model_config = ConfigDict(extra="forbid", from_attributes=True)
