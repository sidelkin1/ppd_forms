import logging
from datetime import datetime, timedelta
from typing import Annotated, cast

import structlog
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocketException,
    status,
)
from jose import JWTError, jwt
from starlette.requests import HTTPConnection

from app.api.dependencies.oauth2 import OAuth2PasswordBearerWithCookie
from app.api.models.auth import Token, User
from app.api.utils.auth import default_verify, ldap_verify
from app.api.utils.dateutil import tz_utc
from app.core.config.settings import Settings

router = APIRouter()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


def get_current_user() -> User:
    raise NotImplementedError


def get_current_user_or_none() -> User | None:
    raise NotImplementedError


class AuthProvider:
    def __init__(self, settings: Settings) -> None:
        self.ldap_url = settings.ldap_url
        self.default_username = settings.app_default_username
        self.default_password = settings.app_default_password
        self.token_expire_time = settings.token_expire_time
        self.secret_key = settings.secret_key
        self.algorithm = "HS256"

    def verify_password(self, username: str, password: str) -> bool:
        return default_verify(
            self.default_username, self.default_password, username, password
        ) or ldap_verify(self.ldap_url, username, password)

    def authenticate_user(self, username: str, password: str) -> User:
        if not self.verify_password(username, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return User(username=username)

    def create_access_token(
        self, data: dict, expires_delta: timedelta
    ) -> Token:
        to_encode = data.copy()
        expire = datetime.now(tz=tz_utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return Token(access_token=encoded_jwt, token_type="bearer")

    def create_user_token(self, user: User) -> Token:
        return self.create_access_token(
            data={"sub": user.username}, expires_delta=self.token_expire_time
        )

    def get_credentials_exception(self, request: HTTPConnection) -> Exception:
        assert request.scope["type"] in ("http", "websocket")
        if request.scope["type"] == "http":
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Could not validate credentials",
        )

    async def get_current_user(
        self,
        token: Annotated[str, Depends(oauth2_scheme)],
        request: HTTPConnection,
    ) -> User:
        credentials_exception = self.get_credentials_exception(request)
        logger.debug("try to check token %s", token)
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            username = cast(str, payload.get("sub"))
            if username is None:
                logger.warning("valid jwt contains no username")
                raise credentials_exception
        except JWTError as error:
            logger.info("invalid jwt", exc_info=error)
            raise credentials_exception
        except Exception as error:
            logger.warning("some jwt error", exc_info=error)
            raise
        structlog.contextvars.bind_contextvars(user_id=username)
        return User(username=username)

    async def get_current_user_or_none(
        self, request: HTTPConnection
    ) -> User | None:
        try:
            token = cast(str, await oauth2_scheme(request))
            user = await self.get_current_user(token, request)
        except HTTPException:
            user = None
        structlog.contextvars.bind_contextvars(
            user_id=user.username if user else None
        )
        return user


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError


UserDep = Annotated[User, Depends(get_current_user)]
UserOrNoneDep = Annotated[User | None, Depends(get_current_user_or_none)]
AuthDep = Annotated[AuthProvider, Depends(get_auth_provider)]
