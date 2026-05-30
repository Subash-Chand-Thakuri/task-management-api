from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.response import ApiResponse
from app.services import auth_service
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(session: DbSession, data: LoginRequest):
    tokens = await auth_service.login(session, data.email, data.password)
    return success_response(
        TokenResponse(**tokens),
        message="Login successful",
    )
