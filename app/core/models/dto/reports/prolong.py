from datetime import date

from pydantic import BaseModel, ConfigDict


class ProlongExpected(BaseModel):
    field: str
    well: str
    date: date
    oil_total_1: float
    oil_total_5: float
    liq_total_1: float
    liq_total_5: float
    report: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
