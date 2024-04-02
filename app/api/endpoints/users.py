from fastapi import APIRouter

from app.api.dependencies.auth import UserDep
from app.api.models.auth import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_me(user: UserDep):
    return user
