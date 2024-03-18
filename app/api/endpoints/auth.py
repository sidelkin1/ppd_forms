from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import AuthDep, UserDep
from app.api.models.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])


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
async def revoke(response: Response, user: UserDep):
    response.delete_cookie(key="access_token", httponly=True)
    return {"message": "Выход из учетной записи!"}
