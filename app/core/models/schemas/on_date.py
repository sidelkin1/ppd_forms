from datetime import date

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, ConfigDict, Field

ON_DATE = date.today().replace(day=1) - relativedelta(months=1)


class OnDate(BaseModel):
    on_date: date = Field(..., examples=[ON_DATE])

    model_config = ConfigDict(extra="forbid")
