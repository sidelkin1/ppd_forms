from datetime import date

from pydantic import BaseModel, ConfigDict


class NewStrategyOilDB(BaseModel):
    id: int | None = None
    field: str
    well: str
    reservoir_before: str
    reservoir_after: str
    vnr_date: date
    gtm_name: str
    start_date: date

    model_config = ConfigDict(extra="forbid", from_attributes=True)
