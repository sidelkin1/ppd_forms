from datetime import date

from pydantic import BaseModel, ConfigDict

from app.core.models.dto.db.validators import EmptyStrOrNanToNone, NanToNone


class NewStrategyInjDB(BaseModel):
    id: int | None = None
    field: str
    well: str
    reservoir: str
    gtm_description: str
    gtm_date: date
    oil_recovery: float | None
    effect_end: NanToNone[date]
    gtm_group: str
    oil_rate: float | None
    gtm_problem: str
    reservoir_neighbs: EmptyStrOrNanToNone[str]
    neighbs: EmptyStrOrNanToNone[str]

    model_config = ConfigDict(extra="forbid", from_attributes=True)
