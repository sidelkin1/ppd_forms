import logging
from datetime import datetime, timedelta
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt

from app.api.dependencies.oauth2 import OAuth2PasswordBearerWithCookie
from app.api.models.auth import Token
from app.api.models.user import User
from app.api.utils.auth import default_verify, ldap_verify
from app.api.utils.dateutil import tz_utc
from app.core.config.settings import Settings

router = APIRouter()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


def get_current_user() -> User:
    raise NotImplementedError


def get_current_user_or_none() -> User:
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

    async def get_current_user(
        self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
        return User(username=username)

    async def get_current_user_or_none(self, request: Request) -> User:
        try:
            token = await oauth2_scheme(request)
            user = await self.get_current_user(token)
        except HTTPException:
            user = None
        return user


def get_auth_provider() -> AuthProvider:
    raise NotImplementedError


UserDep = Annotated[User, Depends(get_current_user)]
UserOrNoneDep = Annotated[User, Depends(get_current_user_or_none)]
AuthDep = Annotated[AuthProvider, Depends(get_auth_provider)]
