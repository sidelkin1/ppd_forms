from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Request, WebSocket


def user_id_provider() -> str:
    raise NotImplementedError


async def get_or_create_user_id(
    request: Request = None,  # type: ignore
    websocket: WebSocket = None,  # type: ignore
) -> str:
    connection = request or websocket
    return connection.session.setdefault("user_id", uuid4().hex)


UserIdDep = Annotated[str, Depends(user_id_provider)]
