from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models.role import Role as RoleModel
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.utils.validators import ensure_found

_NOT_FOUND = "User not found"


async def list_users(session: AsyncSession) -> list[UserRead]:
    result = await session.execute(select(UserModel).order_by(UserModel.id))
    return [UserRead.model_validate(user) for user in result.scalars().all()]


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
    role = await session.get(RoleModel, data.role_id)
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
        role_id=data.role_id,
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
