from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies.auth import UserOrNoneDep
from app.api.utils.redirect import build_redirect_response

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse("/reports")


@router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, user: UserOrNoneDep):
    if user is None:
        return build_redirect_response(request, "login_page")
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
        {
            "path": "opp_per_year",
            "title": "Количество ОПП за год",
            "description": (
                r"Количество ОПП за год:"
                r"<ul>"
                r"<li>общее число исследований</li>"
                r"<li>число охваченных скважин</li>"
                r"</ul>"
            ),
        },
    )
    return templates.TemplateResponse(
        "reports/report_list.html",
        {"request": request, "reports": reports, "user": user},
    )


@router.get("/tables", response_class=HTMLResponse)
async def tables(request: Request, user: UserOrNoneDep):
    if user is None:
        return build_redirect_response(request, "login_page")
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
        {"request": request, "tables": tables, "user": user},
    )
