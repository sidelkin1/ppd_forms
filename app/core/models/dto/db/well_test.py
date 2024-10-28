from datetime import date

from pydantic import BaseModel, ConfigDict

from app.core.models.dto.db.validators import EmptyStrOrNanToNone


class WellTestDB(BaseModel):
    id: int | None = None
    well: str
    field: str
    reservoir: str
    well_type: EmptyStrOrNanToNone[str]
    well_test: str
    start_date: date
    end_date: date
    oil_perm: EmptyStrOrNanToNone[float]
    wat_perm: EmptyStrOrNanToNone[float]
    liq_perm: EmptyStrOrNanToNone[float]
    skin_factor: EmptyStrOrNanToNone[float]
    resp_owc: EmptyStrOrNanToNone[float]
    prod_index: EmptyStrOrNanToNone[float]
    frac_length: EmptyStrOrNanToNone[float]
    reliability: EmptyStrOrNanToNone[str]

    model_config = ConfigDict(extra="forbid", from_attributes=True)
