from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies.user import UserIdDep

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/")
async def home():
    return RedirectResponse("/reports")


@router.get("/reports")
async def reports(request: Request, user_id: UserIdDep):
    reports = (
        {
            "path": "profile",
            "title": "Профили добычи/закачки",
            "description": "Какое-то краткое описание отчета.",
        },
        {
            "path": "oil_loss",
            "title": "Потери по базе ГТМ ППД",
            "description": "Какое-то краткое описание отчета.",
        },
    )
    return templates.TemplateResponse(
        "reports/report_list.html",
        context={"request": request, "reports": reports},
    )


@router.get("/tables")
async def tables(request: Request, user_id: UserIdDep):
    tables = (
        {
            "path": "report",
            "title": "МЭР",
            "source": "database",
            "description": "Какое-то краткое описание таблицы.",
        },
        {
            "path": "profile",
            "title": "ОПП",
            "source": "database",
            "description": "Какое-то краткое описание таблицы.",
        },
        {
            "path": "ns_ppd",
            "title": "НС ППД",
            "source": "excel",
            "description": "Какое-то краткое описание таблицы.",
        },
        {
            "path": "ns_oil",
            "title": "НС НФ",
            "source": "excel",
            "description": "Какое-то краткое описание таблицы.",
        },
        {
            "path": "inj_db",
            "title": "База ГТМ ППД",
            "source": "excel",
            "description": "Какое-то краткое описание таблицы.",
        },
        {
            "path": "neighbs",
            "title": "Округа",
            "source": "excel",
            "description": "Какое-то краткое описание таблицы.",
        },
    )
    return templates.TemplateResponse(
        "tables/table_list.html",
        context={"request": request, "tables": tables},
    )
