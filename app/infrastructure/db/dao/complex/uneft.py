from dataclasses import dataclass

from app.core.models.dto import UneftFieldDB, UneftReservoirDB, UneftWellDB
from app.infrastructure.db.dao.sql import ofm


@dataclass
class UneftDAO:
    fields: ofm.FieldListDAO
    reservoirs: ofm.ReservoirListDAO
    wells: ofm.WellListDAO

    async def get_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_fields()

    async def get_production_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_production_fields()

    async def get_injection_fields(self) -> list[UneftFieldDB]:
        return await self.fields.get_injection_fields()

    async def get_reservoirs(self, field_id: int) -> list[UneftReservoirDB]:
        return await self.reservoirs.get_reservoirs(field_id)

    async def get_production_wells(self, field_id: int) -> list[UneftWellDB]:
        return await self.wells.get_production_wells(field_id)

    async def get_injection_wells(self, field_id: int) -> list[UneftWellDB]:
        return await self.wells.get_injection_wells(field_id)

    async def get_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_field(field_id)

    async def get_production_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_production_field(field_id)

    async def get_injection_field(self, field_id: int) -> UneftFieldDB | None:
        return await self.fields.get_injection_field(field_id)
