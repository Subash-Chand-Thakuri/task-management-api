from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.core.security import bearer_scheme
from app.db.session import get_session
from app.models.role import Role as RoleModel
from app.models.role import RoleNameEnum
from app.schemas.user import UserRead
from app.services.auth_service import get_user_from_token
from app.utils.validators import ensure_found

DbSession = Annotated[AsyncSession, Depends(get_session)]


@dataclass
class AuthContext:
    """Authenticated user plus resolved role (after JWT + DB checks)."""

    user: UserRead
    role: RoleNameEnum


async def get_auth_context(
    session: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> AuthContext:
    user = await get_user_from_token(session, credentials.credentials)
    role = await session.get(RoleModel, user.role_id)
    ensure_found(role, "Role not found")
    return AuthContext(user=user, role=role.name)

# Authenticated user context
RequireAuth = Annotated[AuthContext, Depends(get_auth_context)]


# Check if user has one of the allowed roles
def require_roles(*allowed: RoleNameEnum) -> Callable:
    allowed_set = set(allowed)

    async def _check(auth: RequireAuth) -> AuthContext:
        if auth.role not in allowed_set:
            raise ForbiddenError("Insufficient permissions")
        return auth

    return _check


require_admin = require_roles(RoleNameEnum.ADMIN)

RequireAdmin = Annotated[AuthContext, Depends(require_admin)]
RequireManagerOrAdmin = Annotated[
    AuthContext,
    Depends(require_roles(RoleNameEnum.ADMIN, RoleNameEnum.MANAGER)),
]
require_any_role = require_roles(
    RoleNameEnum.ADMIN,
    RoleNameEnum.MANAGER,
    RoleNameEnum.USER,
)

RequireAnyRole = Annotated[AuthContext, Depends(require_any_role)]
