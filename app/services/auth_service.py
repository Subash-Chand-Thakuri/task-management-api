from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, decode_access_token, verify_password
from app.models.user import User as UserModel
from app.schemas.user import UserRead


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> UserModel | None:
    result = await session.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password):
        return None
    return user


async def login(session: AsyncSession, email: str, password: str) -> dict[str, str]:
    user = await authenticate_user(session, email, password)
    if user is None:
        raise UnauthorizedError("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


async def get_user_from_token(session: AsyncSession, token: str) -> UserRead:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid token payload")

    user = await session.get(UserModel, int(user_id))
    if user is None:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")

    return UserRead.model_validate(user)
