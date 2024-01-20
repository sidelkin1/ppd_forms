from fastapi import APIRouter

from app.api.endpoints.database import router as database_router
from app.api.endpoints.excel import router as excel_router
from app.api.endpoints.home import router as home_router
from app.api.endpoints.job import router as job_router
from app.api.endpoints.report import router as report_router
from app.api.endpoints.uneft import router as uneft_router

main_router = APIRouter()
main_router.include_router(home_router, tags=["home"])
main_router.include_router(
    database_router, prefix="/database", tags=["database"]
)
main_router.include_router(report_router, prefix="/reports", tags=["reports"])
main_router.include_router(job_router, prefix="/jobs", tags=["jobs"])
main_router.include_router(excel_router, prefix="/excel", tags=["excel"])
main_router.include_router(uneft_router, prefix="/uneft", tags=["uneft"])
