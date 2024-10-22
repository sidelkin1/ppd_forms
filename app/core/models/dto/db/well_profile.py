from datetime import date

from pydantic import BaseModel, ConfigDict

from app.core.models.dto.db.validators import EmptyStrToNone


class WellProfileDB(BaseModel):
    id: int | None = None
    field: str
    uwi: str
    well_name: str
    well_type: EmptyStrToNone[str]
    rec_date: date
    cid_all: str
    cid_layer: EmptyStrToNone[str]
    layer: EmptyStrToNone[str]
    top: float
    bottom: float
    abstop: EmptyStrToNone[float]
    absbotm: EmptyStrToNone[float]
    diff_absorp: EmptyStrToNone[float]
    tot_absorp: EmptyStrToNone[float]
    liq_rate: EmptyStrToNone[float]
    remarks: EmptyStrToNone[str]

    model_config = ConfigDict(extra="forbid", from_attributes=True)
