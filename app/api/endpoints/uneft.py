from fastapi import APIRouter

from app.api.dependencies.dao.provider import HolderDep
from app.api.utils.validators import check_field_exists
from app.core.models.dto import FieldListDB, ReservoirListDB

router = APIRouter()


@router.get("/fields", response_model=list[FieldListDB])
async def field_list(holder: HolderDep):
    fields = await holder.ofm_field_list.get_by_params()
    return fields


@router.get("/fields/{field_id}", response_model=list[ReservoirListDB])
async def reservoir_list(field_id: int, holder: HolderDep):
    fields = await holder.ofm_field_list.get_by_params()
    check_field_exists(field_id, fields)
    reservoirs = await holder.ofm_reservoir_list.get_by_params(
        field_id=field_id
    )
    return reservoirs
