from dataclasses import dataclass

from app.core.models.dto import UneftFieldDB, UneftReservoirDB
from app.infrastructure.db.dao.sql import ofm
from app.infrastructure.db.dao.sql.reporters.ofm import OfmBaseDAO


@dataclass
class UneftDAO(OfmBaseDAO):
    fields: ofm.FieldListDAO
    reservoirs: ofm.ReservoirListDAO

    async def get_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_fields()

    async def get_production_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_production_fields()

    async def get_injection_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_injection_fields()

    async def get_reservoirs(self) -> list[UneftReservoirDB]:
        return await self.reservoirs.get_by_params()

    async def get_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_field(field_id)

    async def get_production_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_production_field(field_id)

    async def get_injection_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_injection_field(field_id)
