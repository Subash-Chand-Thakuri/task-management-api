from typing import Literal

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AuthContext
from app.core.exceptions import ConflictError, ValidationAppError
from app.core.security import hash_password
from app.models.role import Role as RoleModel
from app.models.role import RoleNameEnum
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.utils.validators import ensure_found

_NOT_FOUND = "User not found"
_SORTABLE_FIELDS = frozenset(
    {"id", "email", "name", "is_active", "role_id", "created_at", "updated_at"}
)

def _apply_user_role_filter(query, auth: AuthContext):
    query = query.join(RoleModel, UserModel.role_id == RoleModel.id)
    if auth.role == RoleNameEnum.ADMIN:
        return query
    if auth.role == RoleNameEnum.MANAGER:
        return query.where(
            or_(
                UserModel.id == auth.user.id,
                RoleModel.name == RoleNameEnum.USER,
            )
        )
    return query.where(UserModel.id == auth.user.id)

async def list_users(
    session: AsyncSession,
    auth: AuthContext,
    *,
    page: int = 1,
    page_size: int = 10,
    sort: str = "id",
    order: Literal["asc", "desc"] = "asc",
    role_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = None,
) -> tuple[list[UserRead], int]:
    query = select(UserModel)

    # filtering and pagination
    query = _apply_user_role_filter(query, auth)

    if role_id is not None:
        query = query.where(UserModel.role_id == role_id)
    if is_active is not None:
        query = query.where(UserModel.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                UserModel.name.ilike(pattern),
                UserModel.email.ilike(pattern),
            )
        )

    if sort not in _SORTABLE_FIELDS:
        raise ValidationAppError(f"Invalid sort field: {sort}")

    sort_column = getattr(UserModel, sort)
    order_clause = asc(sort_column) if order == "asc" else desc(sort_column)

    total = (
        await session.execute(select(func.count()).select_from(query.subquery()))
    ).scalar_one()

    result = await session.execute(
        query.order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    users = [UserRead.model_validate(user) for user in result.scalars().all()]
    return users, total


async def get_user_by_id(session: AsyncSession, user_id: int) -> UserRead:
    user = await session.get(UserModel, user_id)
    ensure_found(user, _NOT_FOUND)
    return UserRead.model_validate(user)


async def get_user_by_email(session: AsyncSession, email: str) -> UserRead:
    result = await session.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalar_one_or_none()
    ensure_found(user, _NOT_FOUND)
    return UserRead.model_validate(user)


async def create_user(session: AsyncSession, data: UserCreate) -> UserRead:
    role_id = data.role_id
    if role_id is None:
        result = await session.execute(
            select(RoleModel).where(RoleModel.name == RoleNameEnum.USER)
        )
        default_role = result.scalar_one_or_none()
        ensure_found(default_role, "Role not found")
        role_id = default_role.id
    else:
        role = await session.get(RoleModel, role_id)
        ensure_found(role, "Role not found")

    existing = await session.execute(
        select(UserModel).where(UserModel.email == data.email)
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("Email already registered")

    user = UserModel(
        email=data.email,
        name=data.name,
        password=hash_password(data.password),
        role_id=role_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


async def update_user(
    session: AsyncSession, user_id: int, data: UserUpdate
) -> UserRead:
    user = await session.get(UserModel, user_id)
    ensure_found(user, _NOT_FOUND)

    updates = data.model_dump(exclude_unset=True)
    if "role_id" in updates:
        role = await session.get(RoleModel, updates["role_id"])
        ensure_found(role, "Role not found")

    if "email" in updates and updates["email"] != user.email:
        existing = await session.execute(
            select(UserModel).where(UserModel.email == updates["email"])
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("Email already registered")

    if "password" in updates:
        updates["password"] = hash_password(updates["password"])

    for field, value in updates.items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


async def delete_user(session: AsyncSession, user_id: int) -> None:
    user = await session.get(UserModel, user_id)
    ensure_found(user, _NOT_FOUND)
    await session.delete(user)
    await session.commit()
