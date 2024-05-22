from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.db.dao.sql.reporters import (
    FnvReporter,
    OppPerYearReporter,
)


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


class FnvMock(FnvReporter):
    fake_cumwat = {
        1: {"field": [1, 1], "uwi": ["F1W1", "F1W2"], "cumwat": [100, 100]}
    }
    fake_layers = {
        1: {
            "cid": ["R1", "R1", "R2", "R2", "R2"],
            "layer_name": ["L1", "L2", "L3", "L4", "L5"],
        }
    }
    fake_poro = {
        "F1W1": {
            "layer_name": ["L1", "L2", "L3", "L4", "L5"],
            "cid": ["R1", "R1", "R2", "R2", "R2"],
            "xcoord": [100, 100, 110, 110, 110],
            "ycoord": [100, 100, 110, 110, 110],
            "ktop": [1, 1.03, 1.09, 1.15, 1.22],
            "kbot": [1.01, 1.05, 1.12, 1.2, 1.24],
            "poro": [0.1, 0.12, 0.14, 0.16, 0.18],
            "knas": [0.5, 0.5, 0.5, 0.5, 0.5],
            "h": [1, 1, 1, 1, 1],
        },
        "F1W2": {
            "layer_name": ["L1", "L3", "L4"],
            "cid": ["R1", "R2", "R2"],
            "xcoord": [500, 550, 550],
            "ycoord": [500, 550, 550],
            "ktop": [1, 1.03, 1.1],
            "kbot": [1.01, 1.05, 1.15],
            "poro": [0.2, 0.15, 0.1],
            "knas": [0.1, 0.1, 0.1],
            "h": [25, 50, 100],
        },
    }
    fake_events = {
        "F1W1": {
            "date_op": [
                datetime(2000, 1, 1),
                datetime(2000, 1, 1),
                datetime(2000, 1, 1),
                datetime(2001, 1, 1),
                datetime(2001, 1, 1),
                datetime(2002, 1, 1),
                datetime(2003, 1, 1),
                datetime(2003, 1, 1),
                datetime(2004, 1, 1),
            ],
            "type_action": [
                "PERFORATION",
                "PERFORATION",
                "PERFORATION",
                "GDI",
                "GDI",
                "SQUEEZE",
                "GDI",
                "GDI",
                "PERFORATION",
            ],
            "top": [1, 1.09, 1.22, 1.02, 1.15, 1.1, 1, 1.2, 1.14],
            "base": [1.05, 1.2, 1.24, 1.1, 1.2, 1.2, 1.05, 1.24, 1.15],
            "prof": [0, 0, 0, 70, 30, 0, 50, 50, 0],
        },
        "F1W2": {
            "date_op": [
                datetime(2000, 1, 1),
                datetime(2001, 1, 1),
                datetime(2002, 1, 1),
                datetime(2003, 1, 1),
                datetime(2004, 1, 1),
                datetime(2005, 1, 1),
            ],
            "type_action": [
                "PERFORATION",
                "PERFORATION",
                "PERFORATION",
                "SQUEEZE",
                "SQUEEZE",
                "SQUEEZE",
            ],
            "top": [1, 1.04, 1.12, 1, 1.04, 1.12],
            "base": [1.04, 1.12, 1.15, 1.04, 1.12, 1.15],
            "prof": [0, 0, 0, 0, 0, 0],
        },
    }
    fake_totwat = {
        "F1W1": {
            "1900-01-01..2000-01-01": None,
            "2000-01-01..2001-01-01": 100,
            "2001-01-01..2002-01-01": 200,
            "2002-01-01..2003-01-01": 100,
            "2003-01-01..2004-01-01": 50,
            "2004-01-01..2010-01-01": 0,
        },
        "F1W2": {
            "1900-01-01..2000-01-01": None,
            "2000-01-01..2001-01-01": 10,
            "2001-01-01..2002-01-01": 10,
            "2002-01-01..2003-01-01": 10,
            "2003-01-01..2004-01-01": 10,
            "2004-01-01..2005-01-01": 10,
            "2005-01-01..2010-01-01": 0,
        },
    }

    def __init__(self, pool: sessionmaker[Session]) -> None:
        pass

    async def cumwat(self, field_id: int) -> pd.DataFrame:
        return pd.DataFrame(self.fake_cumwat[field_id])

    async def layers(self, field_id: int) -> pd.DataFrame:
        return pd.DataFrame(self.fake_layers[field_id])

    async def poro(self, uwi: str) -> pd.DataFrame:
        return pd.DataFrame(self.fake_poro[uwi])

    async def events(self, alternative: bool, uwi: str) -> pd.DataFrame:
        return pd.DataFrame(self.fake_events[uwi])

    async def totwat(self, uwi: str, date_from: str, date_to: str) -> float:
        totwat = self.fake_totwat[uwi].get("..".join((date_from, date_to)))
        return totwat or 0
