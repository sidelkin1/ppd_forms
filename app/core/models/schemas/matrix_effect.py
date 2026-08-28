from datetime import date
from typing import Self

from dateutil.relativedelta import relativedelta
from pydantic import Field, PositiveInt, model_validator

from app.core.models.enums import ExcludeGTM
from app.core.models.schemas.date_range import DateRange

ON_DATE = date.today().replace(day=1) - relativedelta(months=1)


class MatrixEffect(DateRange):
    base_period: PositiveInt = Field(..., examples=[1])
    pred_period: PositiveInt | None = Field(None, examples=[12])
    excludes: list[ExcludeGTM] = Field(..., examples=[[ExcludeGTM.perf]])
    on_date: date | None = Field(None, examples=[ON_DATE])
    wells: str | None = None

    @model_validator(mode="after")
    def check_fields_not_both_none(self) -> Self:
        if self.pred_period is None and self.on_date is None:
            raise ValueError("`pred_period` and `on_date` cannot both be None")
        return self
