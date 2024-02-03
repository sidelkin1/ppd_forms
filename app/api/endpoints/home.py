from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.api.dependencies.auth import AuthDep, UserOrNoneDep
from app.api.dependencies.path import PathDep
from app.api.endpoints.auth import revoke, token
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


@router.get("/login")
async def login_page(
    request: Request, username: str = "", error: bool = False
):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "error": error, "username": username},
    )


@router.get("/logout")
async def logout_page(request: Request):
    response = templates.TemplateResponse(
        "auth/logout.html", {"request": request}
    )
    await revoke(response)
    return response


@router.post("/login")
async def login(
    request: Request,
    auth: AuthDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    next: str = "",
):
    response = RedirectResponse(
        next or request.url_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )
    try:
        await token(response, auth, form_data)
    except HTTPException:
        return RedirectResponse(
            request.url_for("login_page").include_query_params(
                username=form_data.username, error=True
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return response
