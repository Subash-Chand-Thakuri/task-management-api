from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role as RoleModel
from app.models.role import RoleNameEnum
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.utils.validators import ensure_found

_NOT_FOUND = "Role not found"


async def list_roles(session: AsyncSession) -> list[Role]:
    result = await session.execute(select(RoleModel).order_by(RoleModel.id))
    return [Role.model_validate(role) for role in result.scalars().all()]


async def get_role_by_id(session: AsyncSession, role_id: int) -> Role:
    role = await session.get(RoleModel, role_id)
    ensure_found(role, _NOT_FOUND)
    return Role.model_validate(role)


async def get_role_by_name(session: AsyncSession, name: RoleNameEnum) -> Role:
    result = await session.execute(select(RoleModel).where(RoleModel.name == name))
    role = result.scalar_one_or_none()
    ensure_found(role, _NOT_FOUND)
    return Role.model_validate(role)


async def create_role(session: AsyncSession, data: RoleCreate) -> Role:
    role = RoleModel(name=data.name)
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return Role.model_validate(role)


async def update_role(session: AsyncSession, role_id: int, data: RoleUpdate) -> Role:
    role = await session.get(RoleModel, role_id)
    ensure_found(role, _NOT_FOUND)
    if data.name is not None:
        role.name = data.name
    await session.commit()
    await session.refresh(role)
    return Role.model_validate(role)


async def delete_role(session: AsyncSession, role_id: int) -> None:
    role = await session.get(RoleModel, role_id)
    ensure_found(role, _NOT_FOUND)
    await session.delete(role)
    await session.commit()
