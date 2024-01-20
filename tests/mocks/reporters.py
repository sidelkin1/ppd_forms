from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters import OppPerYearReporter


class OppPerYearMock(OppPerYearReporter):
    def __init__(self, pool: sessionmaker[Session]) -> None:
        pass

    async def read_one(
        self, *, key: str | None = None, **params
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "field": ["F1", "F2"],
                "well_name": ["W1", "W2"],
                "well_type": ["Prod", "Inj"],
                "rec_date": [datetime(2000, 1, 1), datetime(2001, 1, 1)],
                "reservoir": ["R1 R2", "R1"],
            }
        )
