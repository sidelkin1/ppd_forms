from fastapi import APIRouter

from app.api.endpoints.database import router as database_router

main_router = APIRouter()
main_router.include_router(
    database_router,
    prefix='/database',
    tags=['database'],
)
# main_router.include_router(
#     donation_router, prefix='/donation', tags=['donations']
# )
