from datetime import date
from typing import TypedDict


class WellTestResult(TypedDict):
    field: str
    reservoir: str
    well: str
    well_type: str
    well_test: str
    end_date: date
    permeability: float | None
    skin_factor: float | None
    resp_owc: float | None
    prod_index: float | None
