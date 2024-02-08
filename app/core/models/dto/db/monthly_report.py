from datetime import date

from pydantic import BaseModel, ConfigDict


class MonthlyReportDB(BaseModel):
    id: int | None = None
    field: str
    well_name: str
    cid_all: str
    cid: str
    dat_rep: date
    oil: float
    oil_v: float
    water_v: float
    water: float
    days: float
    cum_oil_v: float
    cum_water_v: float
    cum_water: float
    oil_fvf: float | None

    model_config = ConfigDict(extra="forbid", from_attributes=True)
