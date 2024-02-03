import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.models.user import User


@pytest.mark.asyncio(scope="session")
async def test_users_me(client: AsyncClient, user: User):
    resp = await client.get("/users/me")
    assert resp.is_success
    data = resp.json()
    assert data == user.model_dump()


@pytest.mark.asyncio(scope="session")
async def test_users_me_not_authenticated(anon_client: AsyncClient):
    resp = await anon_client.get("/users/me")
    assert not resp.is_success
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
