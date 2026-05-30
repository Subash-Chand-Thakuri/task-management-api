from fastapi import APIRouter

from app.schemas.user import User
from app.services.user_service import get_dummy_users


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User])
async def list_users():
    return get_dummy_users()
