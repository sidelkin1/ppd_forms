import structlog
from starlette.types import ASGIApp, Receive, Scope, Send


class StructlogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=scope["request_id"])
        await self.app(scope, receive, send)
