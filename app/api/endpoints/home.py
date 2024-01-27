from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies.settings import SettingsDep
from app.api.dependencies.user import UserIdDep
from app.core.config.parsers.file_reader import read_config

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse("/reports")


@router.get("/reports", response_class=HTMLResponse)
async def reports(
    request: Request,
    user_id: UserIdDep,
    settings: SettingsDep,
):
    reports = read_config(settings.report_config_file)
    return templates.TemplateResponse(
        "reports/report_list.html",
        context={"request": request, "reports": reports},
    )


@router.get("/tables", response_class=HTMLResponse)
async def tables(
    request: Request,
    user_id: UserIdDep,
    settings: SettingsDep,
):
    tables = read_config(settings.table_config_file)
    return templates.TemplateResponse(
        "tables/table_list.html",
        context={"request": request, "tables": tables},
    )
