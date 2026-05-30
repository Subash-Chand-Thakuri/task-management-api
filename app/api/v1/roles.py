from fastapi import APIRouter, Depends, status

from app.api.deps import DbSession, RequireAdmin, get_auth_context
from app.schemas.response import ApiResponse
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.services import role_service
from app.utils.responses import success_response
from app.utils.validators import ensure_positive_id

router = APIRouter(prefix="/roles", tags=["roles"])

public_router = APIRouter()


@public_router.get("/", response_model=ApiResponse[list[Role]])
async def list_roles(session: DbSession):
    roles = await role_service.list_roles(session)
    return success_response(roles)


@public_router.get("/{role_id}", response_model=ApiResponse[Role])
async def get_role(session: DbSession, role_id: int):
    ensure_positive_id(role_id, field="role_id")
    role = await role_service.get_role_by_id(session, role_id)
    return success_response(role)


protected_router = APIRouter(dependencies=[Depends(get_auth_context)])


@protected_router.post(
    "/",
    response_model=ApiResponse[Role],
    status_code=status.HTTP_201_CREATED,
)
async def create_role(session: DbSession, data: RoleCreate, auth: RequireAdmin):
    role = await role_service.create_role(session, data)
    return success_response(role, message="Role created")


@protected_router.put("/{role_id}", response_model=ApiResponse[Role])
async def update_role(
    session: DbSession,
    role_id: int,
    data: RoleUpdate,
    auth: RequireAdmin,
):
    ensure_positive_id(role_id, field="role_id")
    role = await role_service.update_role(session, role_id, data)
    return success_response(role, message="Role updated")


@protected_router.delete("/{role_id}", response_model=ApiResponse[None])
async def delete_role(session: DbSession, role_id: int, auth: RequireAdmin):
    ensure_positive_id(role_id, field="role_id")
    await role_service.delete_role(session, role_id)
    return success_response(message="Role deleted")


router.include_router(public_router)
router.include_router(protected_router)
