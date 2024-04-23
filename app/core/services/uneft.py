from typing import cast

from app.core.models.dto import UneftFieldDB
from app.core.models.enums import WellStock
from app.infrastructure.db.dao.complex.uneft import UneftDAO


async def uneft_fields(
    stock: WellStock, field_id: int | None, dao: UneftDAO
) -> UneftFieldDB | list[UneftFieldDB] | None:
    match stock, field_id:
        case WellStock.all, None:
            return await dao.get_fields()
        case WellStock.all, field_id:
            return await dao.get_field(cast(int, field_id))
        case WellStock.production, None:
            return await dao.get_production_fields()
        case WellStock.production, field_id:
            return await dao.get_production_field(cast(int, field_id))
        case WellStock.injection, None:
            return await dao.get_injection_fields()
        case WellStock.injection, field_id:
            return await dao.get_injection_field(cast(int, field_id))
    raise ValueError("Unsupported input arguments!")
