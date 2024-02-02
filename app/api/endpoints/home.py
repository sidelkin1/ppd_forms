from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies.auth import UserOrNoneDep
from app.api.dependencies.path import PathDep
from app.api.utils.redirect import build_redirect_response
from app.core.config.parsers.file_reader import read_config

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    return RedirectResponse("/reports")


@router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, user: UserOrNoneDep, path: PathDep):
    if user is None:
        return build_redirect_response(request, "login_page")
    reports = read_config(path.report_config_file)
    return templates.TemplateResponse(
        "reports/report_list.html",
        {"request": request, "reports": reports, "user": user},
    )


@router.get("/tables", response_class=HTMLResponse)
async def tables(request: Request, user: UserOrNoneDep, path: PathDep):
    if user is None:
        return build_redirect_response(request, "login_page")
    tables = read_config(path.table_config_file)
    return templates.TemplateResponse(
        "tables/table_list.html",
        {"request": request, "tables": tables, "user": user},
    )
