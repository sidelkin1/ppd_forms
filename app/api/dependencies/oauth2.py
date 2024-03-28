from typing import Any, cast

from fastapi import HTTPException, WebSocketException, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import HTTPConnection


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes})
        )
        super().__init__(
            flows=flows, scheme_name=scheme_name, auto_error=auto_error
        )

    def get_authorization_exception(
        self, request: HTTPConnection
    ) -> Exception:
        assert request.scope["type"] in ("http", "websocket")
        if request.scope["type"] == "http":
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Not authenticated",
        )

    async def __call__(self, request: HTTPConnection) -> str | None:
        authorization = request.cookies.get("access_token")
        scheme, param = get_authorization_scheme_param(authorization)
        authorization_exception = self.get_authorization_exception(request)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise authorization_exception
            else:
                return None
        return param
