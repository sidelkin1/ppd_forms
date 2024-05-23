from sqlalchemy.orm import Session

from app.core.models.dto import UneftFieldDB, UneftReservoirDB, UneftWellDB
from app.infrastructure.db.dao.sql.ofm import (
    FieldListDAO,
    ReservoirListDAO,
    WellListDAO,
)


class FieldListMock(FieldListDAO):
    fake_fields = {
        1: UneftFieldDB(id=1, name="F1"),
        2: UneftFieldDB(id=2, name="F2"),
    }

    def __init__(self, session: Session) -> None:
        pass

    async def get_fields(self) -> list[UneftFieldDB]:
        return list(self.fake_fields.values())

    async def get_production_fields(self) -> list[UneftFieldDB]:
        return [self.fake_fields[1]]

    async def get_injection_fields(self) -> list[UneftFieldDB]:
        return [self.fake_fields[2]]

    async def get_field(self, field_id: int) -> UneftFieldDB | None:
        return self.fake_fields.get(field_id)

    async def get_production_field(self, field_id: int) -> UneftFieldDB | None:
        return self.fake_fields[1] if field_id == 1 else None

    async def get_injection_field(self, field_id: int) -> UneftFieldDB | None:
        return self.fake_fields[2] if field_id == 2 else None


class ReservoirListMock(ReservoirListDAO):
    fake_reservoirs = {
        1: [
            UneftReservoirDB(id=1, name="R1"),
            UneftReservoirDB(id=2, name="R2"),
        ],
        2: [UneftReservoirDB(id=1, name="R1")],
    }

    def __init__(self, session: Session) -> None:
        pass

    async def get_reservoirs(self, field_id: int) -> list[UneftReservoirDB]:
        return self.fake_reservoirs.get(field_id) or []


class WellListMock(WellListDAO):
    fake_wells = {
        1: [
            UneftWellDB(uwi="F1W1", name="W1"),
            UneftWellDB(uwi="F1W2", name="W2"),
        ],
        2: [UneftWellDB(uwi="F2W1", name="W1")],
    }

    def __init__(self, session: Session) -> None:
        pass

    async def get_production_wells(self, field_id: int) -> list[UneftWellDB]:
        return self.fake_wells.get(field_id) or []

    async def get_injection_wells(self, field_id: int) -> list[UneftWellDB]:
        return self.fake_wells.get(field_id) or []
