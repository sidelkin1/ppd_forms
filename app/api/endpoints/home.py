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
            "description": (
                r"Распределение добычи/закачки по пластам, построенное"
                r"<ul>"
                r"<li>на последний ненулевой МЭР</li>"
                r"<li>на последнее информативное ОПП</li>"
                r"</ul>"
            ),
        },
        {
            "path": "oil_loss",
            "title": "Потери по базе ГТМ ППД",
            "description": (
                r"Потери дебита нефти по факторам"
                r" дебита жидкости и обводненности:"
                r"<ul>"
                r"<li>начальная точка соответствует"
                r" первому ненулевому МЭР</li>"
                r"<li>конечная точка соответствует"
                r" последней дате интервала</li>"
                r"</ul>"
            ),
            "loss_mode": {
                "selected": "--Выберите режим выгрузки--",
                "options": [
                    {"value": "first_rate", "text": "Qн на начало периода"},
                    {"value": "max_rate", "text": "Максимальный Qн"},
                ],
            },
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
