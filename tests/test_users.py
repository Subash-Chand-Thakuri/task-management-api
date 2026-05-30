from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.api.deps import AuthContext
from app.core.exceptions import ConflictError
from app.main import app
from app.models.role import RoleNameEnum
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserRead
from app.services import user_service


def _auth(role: RoleNameEnum, *, user_id: int = 1) -> AuthContext:
    user = UserRead(
        id=user_id,
        email="actor@example.com",
        name="Actor",
        is_active=True,
        role_id=1,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )
    return AuthContext(user=user, role=role)


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_users_user_role_sees_only_themselves():
    query = user_service._apply_user_role_filter(
        select(UserModel), _auth(RoleNameEnum.USER, user_id=7)
    )
    sql = str(query.compile(compile_kwargs={"literal_binds": True}))

    assert "users.id = 7" in sql


@pytest.mark.asyncio
async def test_create_user_raises_conflict_for_duplicate_email():
    session = MagicMock()

    role_result = MagicMock()
    role_result.scalar_one_or_none.return_value = MagicMock(id=3)

    existing_result = MagicMock()
    existing_result.scalar_one_or_none.return_value = MagicMock()

    session.execute = AsyncMock(side_effect=[role_result, existing_result])

    data = UserCreate(email="taken@example.com", name="Dup", password="secret123")

    with pytest.raises(ConflictError, match="Email already registered"):
        await user_service.create_user(session, data)

    session.add.assert_not_called()
