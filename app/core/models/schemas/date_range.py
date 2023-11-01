from datetime import date

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, Field

FROM_TIME = date.today().replace(day=1) - relativedelta(months=12)
TO_TIME = date.today().replace(day=1) - relativedelta(months=1)


class DateRange(BaseModel):
    date_from: date = Field(..., examples=[FROM_TIME])
    date_to: date = Field(..., examples=[TO_TIME])

    model_config = ConfigDict(extra="forbid")
