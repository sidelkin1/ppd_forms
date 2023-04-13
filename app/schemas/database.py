from datetime import date

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Extra, Field

FROM_TIME = (
    date.today().replace(day=1) - relativedelta(months=12)
)

TO_TIME = (
    date.today().replace(day=1) - relativedelta(months=1)
)


class DateRange(BaseModel):
    date_from: date = Field(..., example=FROM_TIME)
    date_to: date = Field(..., example=TO_TIME)

    class Config:
        extra = Extra.forbid
