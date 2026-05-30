from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import (
    DbSession,
    RequireAdmin,
    RequireAuth,
    RequireAnyRole,
    RequireManagerOrAdmin,
    get_auth_context,
)
from app.schemas.response import ApiResponse, PaginatedData
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service
from app.utils.responses import paginated_response, success_response
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


@protected_router.get("/", response_model=ApiResponse[PaginatedData[UserRead]])
async def list_users(
    session: DbSession,
    auth: RequireAnyRole,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    sort: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    role_id: int | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
):
    users, total = await user_service.list_users(
        session,
        auth,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
        role_id=role_id,
        is_active=is_active,
        search=search,
    )
    return paginated_response(users, page=page, page_size=page_size, total=total)


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
