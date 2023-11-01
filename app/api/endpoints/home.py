from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.api.dependencies.user import UserIdDep

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/")
async def home(request: Request, user_id: UserIdDep):
    return templates.TemplateResponse(
        "home.html", context={"request": request}
    )
