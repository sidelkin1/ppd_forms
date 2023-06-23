from fastapi import APIRouter

from app.api.endpoints.database import router as database_router
from app.api.endpoints.report import router as report_router

main_router = APIRouter()
main_router.include_router(
    database_router,
    prefix='/database',
    tags=['database'],
)
main_router.include_router(
    report_router,
    prefix='/report',
    tags=['reports']
)
