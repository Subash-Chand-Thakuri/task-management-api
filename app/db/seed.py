"""Idempotent database seed: roles (admin, manager, user) and default admin user."""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.role import Role, RoleNameEnum
from app.models.user import User

logger = logging.getLogger(__name__)

ROLES_TO_SEED = (RoleNameEnum.ADMIN, RoleNameEnum.MANAGER, RoleNameEnum.USER)


async def _get_role_by_name(session: AsyncSession, name: RoleNameEnum) -> Role | None:
    result = await session.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def _get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def ensure_role(session: AsyncSession, name: RoleNameEnum) -> Role:
    """Create role only when no row exists with this name."""
    existing = await _get_role_by_name(session, name)
    if existing is not None:
        logger.info("Role already exists, skipping: %s", name.value)
        return existing

    role = Role(name=name)
    session.add(role)
    await session.flush()
    logger.info("Created role: %s", name.value)
    return role


async def ensure_admin_user(session: AsyncSession, admin_role: Role) -> None:
    """Create admin user only when no row exists with this email."""
    existing = await _get_user_by_email(session, settings.admin_email)
    if existing is not None:
        logger.info("Admin user already exists, skipping: %s", settings.admin_email)
        return

    session.add(
        User(
            email=settings.admin_email,
            name=settings.admin_name,
            password=hash_password(settings.admin_password),
            is_active=True,
            role_id=admin_role.id,
        )
    )
    logger.info("Created admin user: %s", settings.admin_email)


async def run_seed() -> None:
    logger.info("Checking seed data (roles + admin user)...")
    async with AsyncSessionLocal() as session:
        roles: dict[RoleNameEnum, Role] = {}
        for role_name in ROLES_TO_SEED:
            roles[role_name] = await ensure_role(session, role_name)

        await ensure_admin_user(session, roles[RoleNameEnum.ADMIN])
        await session.commit()

    logger.info("Seed completed.")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
