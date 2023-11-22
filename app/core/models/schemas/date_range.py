from datetime import date
from typing import Self

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, Field, model_validator

FROM_TIME = date.today().replace(day=1) - relativedelta(months=12)
TO_TIME = date.today().replace(day=1) - relativedelta(months=1)


class DateRange(BaseModel):
    date_from: date = Field(..., examples=[FROM_TIME])
    date_to: date = Field(..., examples=[TO_TIME])

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def check_date_ordering(self) -> Self:
        if self.date_from > self.date_to:
            raise ValueError(
                "`date_from` must be less than or equal to `date_to`"
            )
        return self
