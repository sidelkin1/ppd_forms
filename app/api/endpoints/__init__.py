from fastapi import FastAPI

from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.database import router as database_router
from app.api.endpoints.excel import router as excel_router
from app.api.endpoints.home import router as home_router
from app.api.endpoints.job import router as job_router
from app.api.endpoints.report import router as report_router
from app.api.endpoints.uneft import router as uneft_router
from app.api.endpoints.users import router as users_router


def setup(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(database_router)
    app.include_router(excel_router)
    app.include_router(home_router)
    app.include_router(job_router)
    app.include_router(report_router)
    app.include_router(uneft_router)
    app.include_router(users_router)
