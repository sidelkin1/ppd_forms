from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.api.dependencies.auth import AuthDep
from app.api.models.auth import Token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/token", response_model=Token)
async def token(
    response: Response,
    auth: AuthDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = auth.authenticate_user(form_data.username, form_data.password)
    token = auth.create_user_token(user)
    response.set_cookie(
        key="access_token", value=f"Bearer {token.access_token}", httponly=True
    )
    return token


@router.post("/revoke", response_model=dict)
async def revoke(response: Response):
    response.delete_cookie(key="access_token", httponly=True)
    return {"message": "Выход из учетной записи!"}


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
