from fastapi import APIRouter, Depends, status

from app.api.deps import (
    DbSession,
    RequireAdmin,
    RequireAuth,
    RequireManagerOrAdmin,
    get_auth_context,
)
from app.schemas.response import ApiResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service
from app.utils.responses import success_response
from app.utils.validators import ensure_positive_id

router = APIRouter(prefix="/users", tags=["users"])

# Public signup — no token
public_router = APIRouter()


@public_router.post(
    "/",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def signup(session: DbSession, data: UserCreate):
    user = await user_service.create_user(session, data)
    return success_response(user, message="User created")


# All routes below require valid JWT (router-level auth)
protected_router = APIRouter(dependencies=[Depends(get_auth_context)])


@protected_router.get("/me", response_model=ApiResponse[UserRead])
async def read_current_user(auth: RequireAuth):
    return success_response(auth.user)


@protected_router.get("/", response_model=ApiResponse[list[UserRead]])
async def list_users(session: DbSession, auth: RequireAdmin):
    users = await user_service.list_users(session)
    return success_response(users)


@protected_router.get("/{user_id}", response_model=ApiResponse[UserRead])
async def get_user(session: DbSession, user_id: int, auth: RequireManagerOrAdmin):
    ensure_positive_id(user_id, field="user_id")
    user = await user_service.get_user_by_id(session, user_id)
    return success_response(user)


@protected_router.put("/{user_id}", response_model=ApiResponse[UserRead])
async def update_user(
    session: DbSession,
    user_id: int,
    data: UserUpdate,
    auth: RequireManagerOrAdmin,
):
    ensure_positive_id(user_id, field="user_id")
    user = await user_service.update_user(session, user_id, data)
    return success_response(user, message="User updated")


@protected_router.delete("/{user_id}", response_model=ApiResponse[None])
async def delete_user(session: DbSession, user_id: int, auth: RequireAdmin):
    ensure_positive_id(user_id, field="user_id")
    await user_service.delete_user(session, user_id)
    return success_response(message="User deleted")


router.include_router(public_router)
router.include_router(protected_router)
