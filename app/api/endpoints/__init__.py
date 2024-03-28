from fastapi import FastAPI

from .auth import router as auth_router
from .database import router as database_router
from .excel import router as excel_router
from .home import router as home_router
from .job import router as job_router
from .report import router as report_router
from .uneft import router as uneft_router
from .users import router as users_router


def setup(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(database_router)
    app.include_router(excel_router)
    app.include_router(home_router)
    app.include_router(job_router)
    app.include_router(report_router)
    app.include_router(uneft_router)
    app.include_router(users_router)
